"""Genera en Word los planes de mejoramiento (uno por aprendiz, cada uno en página nueva).
Uso: python generar_plan_mejoramiento.py --datos planes.json --salida <ruta>.docx [--plantilla <GFPI-F-135.docx>]
Usa el logo, encabezado, estilos y márgenes de la plantilla GFPI-F-135 de la skill guia-aprendizaje-sena,
con pie propio. El JSON base lo crea consolidar_juicios.py --planes. Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nucleo  # noqa: E402

nucleo.scripts_guia()
from generar_instrumentos import (ANCHO, CASILLA, GRIS, GRIS_OSCURO, PENDIENTE, celda, para, run,  # noqa: E402
                                  ruta_plantilla, tabla)

PIE = "Plan de mejoramiento – Formación Profesional Integral SENA"
CAMPOS_ID = {"programa", "codigo_version", "ficha", "competencia", "instructor", "fecha"}
CAMPOS_PLAN = {"aprendiz", "documento", "resultados", "compromisos"}
CAMPOS_RA = {"ra", "criterios", "evidencias_no_aprobadas", "actividades", "evidencia_mejoramiento", "fecha_entrega"}


def v(x, blank=False):
    if x is None or (isinstance(x, (str, list)) and not x):
        return "" if blank else PENDIENTE
    return "\n".join(map(str, x)) if isinstance(x, list) else str(x)


def plan(ident, p, primero):
    if set(p) - CAMPOS_PLAN:
        raise ValueError("Campos de plan no válidos: " + ", ".join(sorted(set(p) - CAMPOS_PLAN)))
    k = 2700
    datos = [("Programa de formación", " – ".join(x for x in (v(ident.get("codigo_version"), True), v(ident.get("programa"))) if x)),
             ("Ficha", v(ident.get("ficha"), True)), ("Competencia", v(ident.get("competencia"))),
             ("Aprendiz", v(p.get("aprendiz"))), ("Documento de identidad", v(p.get("documento"), True)),
             ("Instructor(a)", v(ident.get("instructor"))), ("Fecha de concertación", v(ident.get("fecha"), True))]
    x = [para("PLAN DE MEJORAMIENTO", jc="center", bold=True, sz=24, after=60, brk=not primero),
         para("Resultados de aprendizaje no aprobados", jc="center", sz=20, after=200),
         tabla([k, ANCHO - k], [[celda(a, k, GRIS, bold=True), celda(b, ANCHO - k)] for a, b in datos]),
         para("", after=0)]
    if not p.get("resultados"):
        raise ValueError(f"{p.get('aprendiz')}: el plan no tiene resultados de aprendizaje.")
    for i, r in enumerate(p["resultados"], 1):
        if set(r) - CAMPOS_RA:
            raise ValueError("Campos de RA no válidos: " + ", ".join(sorted(set(r) - CAMPOS_RA)))
        acts = r.get("actividades") or []
        filas = [[celda(f"Resultado de aprendizaje {i}", ANCHO, GRIS_OSCURO, span=2, bold=True)],
                 [celda(v(r.get("ra")), ANCHO, span=2)],
                 [celda("Criterios de evaluación", k, GRIS, bold=True), celda(["• " + c for c in r.get("criterios") or []] or [PENDIENTE], ANCHO - k)],
                 [celda("Evidencias no aprobadas", k, GRIS, bold=True), celda(v(r.get("evidencias_no_aprobadas")), ANCHO - k)],
                 [celda("Actividades de mejoramiento", k, GRIS, bold=True),
                  celda([f"{j}. {a}" for j, a in enumerate(acts, 1)] or [PENDIENTE], ANCHO - k)],
                 [celda("Evidencia a entregar", k, GRIS, bold=True), celda(v(r.get("evidencia_mejoramiento")), ANCHO - k)],
                 [celda("Fecha límite de entrega", k, GRIS, bold=True), celda(v(r.get("fecha_entrega")), ANCHO - k)],
                 [celda("Resultado del plan", k, GRIS, bold=True),
                  celda(f"{CASILLA} Aprobado     {CASILLA} No aprobado     Fecha: ________", ANCHO - k)]]
        x += [tabla([k, ANCHO - k], filas), para("", after=0)]
    x += [para("Compromisos del aprendiz", bold=True, keep=True, after=60),
          para(v(p.get("compromisos")), jc="both"),
          tabla([ANCHO], [[celda("Observaciones del seguimiento:", ANCHO, bold=True, alto_vacio=True)]]),
          para("", after=240)]
    m = ANCHO // 2
    x.append(tabla([m, ANCHO - m], [[celda(["", "", "_" * 34, "Firma del instructor(a)"], m, jc="center"),
                                     celda(["", "", "_" * 34, "Firma del aprendiz"], ANCHO - m, jc="center")]]))
    return "".join(x)


def generar(datos, salida, plantilla_ruta=None):
    if set(datos) - {"identificacion", "planes"}:
        raise ValueError("El JSON solo admite «identificacion» y «planes».")
    ident = datos.get("identificacion") or {}
    if set(ident) - CAMPOS_ID:
        raise ValueError("Campos de identificación no válidos: " + ", ".join(sorted(set(ident) - CAMPOS_ID)))
    planes = datos.get("planes") or []
    if not planes:
        raise ValueError("No hay planes: ningún aprendiz tiene RA no aprobados.")
    plantilla = ruta_plantilla(plantilla_ruta)
    salida = Path(salida).resolve()
    with ZipFile(plantilla) as z:
        entradas = [(i, z.read(i.filename)) for i in z.infolist()]
    partes = dict((i.filename, b) for i, b in entradas)
    doc = partes["word/document.xml"].decode("utf-8")
    inicio = doc[:doc.index("<w:body>") + len("<w:body>")]
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S).group(0)
    cuerpo = "".join(plan(ident, p, i == 0) for i, p in enumerate(planes))
    nuevo = (inicio + cuerpo + sect + "</w:body></w:document>").encode("utf-8")
    pie = partes["word/footer1.xml"].decode("utf-8")
    pie, n = re.subn(r"<w:r>\s*<w:t>GFPI-F-</w:t>.*?<w:t>04</w:t></w:r>", run(PIE, sz=18), pie, flags=re.S)
    if n != 1:
        raise ValueError("El pie de la plantilla no tiene la estructura esperada.")
    cambiados = {"word/document.xml": nuevo, "word/footer1.xml": pie.encode("utf-8")}
    for c in cambiados.values():
        minidom.parseString(c)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(salida, "w") as z:
        for info, contenido in entradas:
            z.writestr(info, cambiados.get(info.filename, contenido))
    return salida


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    ap.add_argument("--plantilla", type=Path)
    a = ap.parse_args()
    try:
        print(generar(json.loads(a.datos.read_text(encoding="utf-8-sig")), a.salida, a.plantilla))
    except ValueError as e:
        raise SystemExit("ERROR: " + str(e))
