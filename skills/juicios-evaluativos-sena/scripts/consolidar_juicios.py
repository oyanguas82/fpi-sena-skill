"""Consolida los juicios evaluativos por resultado de aprendizaje (RA) a partir de las evidencias.
Uso: python consolidar_juicios.py --datos juicios.json --salida <ruta>.xlsx [--programa <programa.json>]
                                 [--planes planes.json]
Regla por RA: APROBADO si todas sus evidencias están aprobadas (A); NO APROBADO si alguna está
no aprobada (D); POR EVALUAR si faltan evidencias y ninguna está en D.
Salida: Excel con hojas Juicios, Evidencias, Resumen; con --planes, el JSON base de los planes de
mejoramiento (aprendices con RA no aprobados, criterios literales del catálogo).
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nucleo  # noqa: E402
import xlsx_simple as xs  # noqa: E402

APROB = {"a", "aprobado", "aprobada", "si", "sí", "cumple", "1", "true"}
NO_APROB = {"d", "no aprobado", "no aprobada", "deficiente", "no", "no cumple", "0", "false"}
CAMPOS_ID = {"programa", "codigo_version", "ficha", "competencia", "instructor", "fecha_corte"}


def estado_ev(v):
    t = str(v if v is not None else "").strip().lower()
    if t in APROB:
        return "A"
    if t in NO_APROB:
        return "D"
    if t in ("", "pendiente", "por evaluar", "-", "none", "null"):
        return ""
    raise ValueError(f"Valor de evidencia no reconocido: «{v}» (use A, D o vacío).")


def juicio(estados):
    if any(e == "D" for e in estados):
        return "NO APROBADO"
    if estados and all(e == "A" for e in estados):
        return "APROBADO"
    return "POR EVALUAR"


def consolidar(datos, prog=None):
    ident = datos.get("identificacion", {})
    if set(ident) - CAMPOS_ID:
        raise ValueError("Campos de identificación no válidos: " + ", ".join(sorted(set(ident) - CAMPOS_ID)))
    ras = datos.get("resultados") or []
    if not ras:
        raise ValueError("«resultados» debe listar los RA con sus evidencias.")
    todas = []
    avisos = []
    for r in ras:
        if not re.match(r"\s*\d{9}\s*-\s*\d{1,2}", str(r.get("codigo", ""))):
            raise ValueError(f"RA «{r.get('codigo')}»: use <competencia>-<nº> (p. ej. 220501096-01).")
        if not r.get("evidencias"):
            raise ValueError(f"RA {r['codigo']}: sin evidencias asociadas.")
        comp, ra = nucleo.buscar_ra(prog, r["codigo"])
        if prog and not ra:
            raise ValueError(f"RA {r['codigo']} no está en el programa.")
        r["_texto"] = nucleo.cap(ra["denominacion"]) if ra else r.get("texto", "")
        r["_criterios"] = [nucleo.cap(x) for x in ((ra or {}).get("criterios_evaluacion") or (comp or {}).get("criterios_evaluacion") or [])]
        todas += [e for e in r["evidencias"] if e not in todas]
    salida = []
    for i, a in enumerate(datos.get("aprendices") or [], 1):
        ev = {k: estado_ev(v) for k, v in (a.get("evidencias") or {}).items()}
        for k in ev:
            if k not in todas:
                avisos.append(f"Aprendiz {i}: la evidencia {k} no está asociada a ningún RA.")
        fila = {"documento": str(a.get("documento", "")), "nombre": a.get("nombre", ""),
                "evidencias": {e: ev.get(e, "") for e in todas}, "juicios": {}, "observaciones": a.get("observaciones", "")}
        for r in ras:
            fila["juicios"][r["codigo"]] = juicio([ev.get(e, "") for e in r["evidencias"]])
        salida.append(fila)
    if not salida:
        raise ValueError("«aprendices» está vacío.")
    return ident, ras, todas, salida, avisos


def excel(ruta, ident, ras, todas, filas):
    titulo = " | ".join(x for x in (ident.get("programa"), ident.get("codigo_version") and f"Programa {ident['codigo_version']}",
                                     ident.get("ficha") and f"Ficha {ident['ficha']}",
                                     ident.get("fecha_corte") and f"Corte {ident['fecha_corte']}") if x)
    enc = ["Documento", "Aprendiz"] + [r["codigo"] for r in ras] + ["Observaciones"]
    j = [enc] + [[f["documento"], f["nombre"]] + [f["juicios"][r["codigo"]] for r in ras] + [f["observaciones"]] for f in filas]
    e = [["Documento", "Aprendiz"] + todas] + [[f["documento"], f["nombre"]] + [f["evidencias"][x] or "" for x in todas] for f in filas]
    res = [["RA", "Resultado de aprendizaje", "Evidencias", "Aprobados", "No aprobados", "Por evaluar"]]
    for r in ras:
        vs = [f["juicios"][r["codigo"]] for f in filas]
        res.append([r["codigo"], r["_texto"], "\n".join(r["evidencias"]), vs.count("APROBADO"),
                    vs.count("NO APROBADO"), vs.count("POR EVALUAR")])
    hojas = [("Juicios", xs.hoja_xml(j, [14, 34] + [16] * len(ras) + [40], "Juicios evaluativos por RA – " + titulo, True)),
             ("Evidencias", xs.hoja_xml(e, [14, 34] + [26] * len(todas), "Estado de evidencias (A aprobada, D no aprobada, vacío pendiente)", True)),
             ("Resumen", xs.hoja_xml(res, [16, 60, 30, 12, 12, 12], "Resumen por resultado de aprendizaje"))]
    return xs.escribir(ruta, hojas)


def planes_base(ident, ras, filas):
    planes = []
    for f in filas:
        pend = [r for r in ras if f["juicios"][r["codigo"]] == "NO APROBADO"]
        if not pend:
            continue
        planes.append({"aprendiz": f["nombre"], "documento": f["documento"], "resultados": [
            {"ra": f"{r['codigo']}. {r['_texto']}".strip(), "criterios": r["_criterios"],
             "evidencias_no_aprobadas": [e for e in r["evidencias"] if f["evidencias"][e] == "D"],
             "actividades": [], "evidencia_mejoramiento": "", "fecha_entrega": ""} for r in pend],
            "compromisos": ""})
    return {"identificacion": {k: ident.get(k, "") for k in ("programa", "codigo_version", "ficha", "competencia", "instructor")}
            | {"fecha": ""}, "planes": planes}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    ap.add_argument("--programa", type=Path)
    ap.add_argument("--planes", type=Path, help="Escribe el JSON base de los planes de mejoramiento")
    a = ap.parse_args()
    datos = json.loads(a.datos.read_text(encoding="utf-8-sig"))
    try:
        prog = nucleo.cargar_programa(a.programa, datos.get("identificacion", {}).get("codigo_version"))
        if prog is None:
            print("AVISO: sin catálogo del programa; los RA no se verifican y los criterios del plan quedan vacíos.")
        ident, ras, todas, filas, avisos = consolidar(datos, prog)
    except ValueError as e:
        raise SystemExit("ERROR: " + str(e))
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    print(excel(a.salida, ident, ras, todas, filas))
    for w in avisos:
        print("AVISO:", w)
    for r in ras:
        vs = [f["juicios"][r["codigo"]] for f in filas]
        print(f"{r['codigo']}: {vs.count('APROBADO')} aprobados, {vs.count('NO APROBADO')} no aprobados, "
              f"{vs.count('POR EVALUAR')} por evaluar")
    if a.planes:
        base = planes_base(ident, ras, filas)
        a.planes.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{a.planes}: {len(base['planes'])} planes de mejoramiento por completar")
