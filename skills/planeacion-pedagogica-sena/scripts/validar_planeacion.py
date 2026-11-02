"""Valida el JSON de la Planeación Pedagógica (GFPI-F-134) y, opcionalmente, el Excel generado.
Uso: python validar_planeacion.py --datos planeacion.json [--programa <programa.json>]
                                  [--proyecto <proyecto.json>] [--xlsx <planeacion.xlsx>]
Comprueba: competencias y RA del catálogo, saberes y criterios literales, actividad de aprendizaje
(verbo en infinitivo + objeto + condición + componente actitudinal), código GA/AA, horas, tipo de
evidencia, AP y fase del proyecto, RA del proyecto sin planear y que el Excel salga de la plantilla.
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_planeacion import (NOMBRE_PLANTILLA, PEND, cargar_programa, competencia,  # noqa: E402
                                resultado, ruta_plantilla)

AA = re.compile(r"^\s*(?:GA\s*(\d+)\s*-\s*(\d{9})\s*-\s*AA\s*(\d+)\s*[:\-]\s*)?(\S+)", re.I)
ACTITUDINAL = re.compile(r"demostrando|actitud|responsab|compromiso|respet|[ée]tic|disposici[oó]n|autonom|"
                         r"colaborativ|rigor|puntualidad|liderazgo|creatividad|disciplina|honestidad|"
                         r"proactiv|trabajo en equipo|asertiv", re.I)
TIPO_EV = re.compile(r"conocimiento|desempe[ñn]o|producto", re.I)


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def literal(txt, oficiales):
    n = norm(txt)
    return n in oficiales or any(len(o) > 20 and (n in o or o in n) for o in oficiales)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def validar(datos, prog, proyecto=None):
    err, av = [], []
    ident = datos.get("identificacion", {})
    for k in ("fecha", "programa", "modalidad", "codigo_version", "equipo", "regional_centro"):
        if not ident.get(k):
            av.append(f"Identificación: falta «{k}» (queda {PEND}).")
    if proyecto and str(ident.get("codigo_proyecto", "")).strip() not in ("", str(proyecto["proyecto"]["codigo"])):
        err.append(f"codigo_proyecto {ident.get('codigo_proyecto')} ≠ proyecto {proyecto['proyecto']['codigo']}.")
    total = 0
    planeados = set()
    for i, f in enumerate(datos.get("filas", []), 1):
        tag = f"Fila {i}"
        try:
            comp = competencia(prog, f.get("competencia", ""))
        except ValueError as e:
            err.append(f"{tag}: {e}")
            continue
        ras = []
        for n in (f.get("resultados") or []):
            try:
                ras.append(resultado(comp, n))
            except ValueError as e:
                err.append(f"{tag}: {e}")
        if not ras:
            err.append(f"{tag}: sin resultados de aprendizaje válidos.")
        for r in ras:
            planeados.add((str(comp["codigo"]), str(r["numero"]).zfill(2)))
        # Selección de saberes y criterios: literal del catálogo (RA o competencia).
        fuentes = {"saberes_conceptos": "conocimientos_saber", "saberes_proceso": "conocimientos_proceso",
                   "criterios": "criterios_evaluacion"}
        for campo, clave in fuentes.items():
            oficiales = {norm(x) for x in comp.get(clave, [])}
            for r in ras:
                oficiales |= {norm(x) for x in r.get(clave, [])}
            for x in f.get(campo) or []:
                if not literal(x, oficiales):
                    err.append(f"{tag}: «{x[:70]}» no está en {clave} del currículo.")
        # Actividad de aprendizaje
        aa = str(f.get("actividad_aprendizaje") or "")
        m = AA.match(aa)
        if not aa.strip():
            err.append(f"{tag}: falta la actividad de aprendizaje.")
        else:
            if m.group(2) and m.group(2) != str(comp["codigo"]):
                err.append(f"{tag}: el código {m.group(2)} de la actividad no es la competencia {comp['codigo']}.")
            if not m.group(1):
                av.append(f"{tag}: la actividad no trae código (GA1-{comp['codigo']}-AA1: …).")
            verbo = norm(m.group(4))
            if not re.search(r"(ar|er|ir)$", verbo):
                err.append(f"{tag}: la actividad debe iniciar con verbo en infinitivo («{m.group(4)}»).")
            if len(aa.split()) < 12:
                av.append(f"{tag}: actividad muy corta; debe tener verbo + objeto + condición + componente actitudinal.")
            if not ACTITUDINAL.search(aa):
                av.append(f"{tag}: la actividad no muestra componente actitudinal (p. ej. «demostrando responsabilidad»).")
        d, ind = num(f.get("horas_directas")), num(f.get("horas_independientes"))
        if d is None or ind is None:
            err.append(f"{tag}: horas directas e independientes deben ser números.")
        else:
            total += d + ind
            horas_ra = [r.get("duracion_horas") for r in ras]
            if all(horas_ra) and horas_ra and d + ind > sum(horas_ra):
                err.append(f"{tag}: {d + ind:g} h superan las {sum(horas_ra)} h de los RA.")
            if comp.get("duracion_horas") and d + ind > comp["duracion_horas"]:
                err.append(f"{tag}: {d + ind:g} h superan las {comp['duracion_horas']} h de la competencia.")
        ev = str(f.get("evidencia") or "")
        if not ev.strip():
            err.append(f"{tag}: falta la descripción de la evidencia.")
        elif not TIPO_EV.search(ev):
            err.append(f"{tag}: la evidencia debe decir si es de conocimiento, desempeño o producto.")
        for k in ("estrategias", "ambiente", "materiales", "instructores"):
            if not str(f.get(k) or "").strip():
                av.append(f"{tag}: falta «{k}».")
        # Proyecto formativo
        if proyecto:
            apm = re.match(r"\s*AP\s*(\d+)", str(f.get("actividad_proyecto") or ""), re.I)
            if not apm:
                err.append(f"{tag}: actividad_proyecto debe iniciar con AP<n>.")
                continue
            ap = next((a for fa in proyecto["fases"] for a in fa["actividades"] if a.get("numero") == int(apm.group(1))), None)
            fase = next((fa["fase"] for fa in proyecto["fases"] for a in fa["actividades"] if a is ap), None)
            if not ap:
                err.append(f"{tag}: AP{apm.group(1)} no existe en el proyecto.")
                continue
            if norm(fase) != norm(f.get("fase", "")):
                err.append(f"{tag}: AP{apm.group(1)} pertenece a la fase {fase}, no a «{f.get('fase')}».")
            en_ap = {(str(x["competencia"]), str(x["ra"]).zfill(2)) for x in ap["resultados"]}
            for r in ras:
                if (str(comp["codigo"]), str(r["numero"]).zfill(2)) not in en_ap:
                    av.append(f"{tag}: RA {comp['codigo']}-{r['numero']} no está planeado en AP{apm.group(1)} del proyecto.")
    if proyecto:
        aps = {int(m.group(1)) for f in datos.get("filas", [])
               for m in [re.match(r"\s*AP\s*(\d+)", str(f.get("actividad_proyecto") or ""), re.I)] if m}
        for fa in proyecto["fases"]:
            for a in fa["actividades"]:
                if a.get("numero") in aps:
                    for x in a["resultados"]:
                        if (str(x["competencia"]), str(x["ra"]).zfill(2)) not in planeados:
                            av.append(f"AP{a['numero']}: RA {x['competencia']}-{x['ra']} del proyecto sin actividad de aprendizaje.")
    return err, av, total


def validar_xlsx(ruta, plantilla_ruta=None):
    err = []
    plantilla = ruta_plantilla(plantilla_ruta)
    with ZipFile(ruta) as z, ZipFile(plantilla) as t:
        nombres = set(z.namelist())
        for n in t.namelist():
            if n not in nombres:
                err.append(f"Excel: falta {n} de la plantilla.")
            elif n.startswith(("xl/media/", "xl/drawings/", "xl/worksheets/sheet1")) and z.read(n) != t.read(n):
                err.append(f"Excel: {n} difiere de la plantilla {NOMBRE_PLANTILLA}.")
        hoja = z.read("xl/worksheets/sheet2.xml").decode("utf-8")
        if "GFPI-F-134" not in hoja or "FASE" not in z.read("xl/workbook.xml").decode("utf-8"):
            err.append("Excel: no conserva el pie GFPI-F-134 o la hoja FASE: genérelo con generar_planeacion.py.")
    return err


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, type=Path)
    ap.add_argument("--programa", type=Path)
    ap.add_argument("--proyecto", type=Path)
    ap.add_argument("--xlsx", type=Path)
    ap.add_argument("--plantilla", type=Path)
    a = ap.parse_args()
    datos = json.loads(a.datos.read_text(encoding="utf-8-sig"))
    try:
        prog = cargar_programa(a.programa, datos.get("identificacion", {}).get("codigo_version"))
    except ValueError as e:
        raise SystemExit("ERROR: " + str(e))
    proy = json.loads(a.proyecto.read_text(encoding="utf-8")) if a.proyecto else None
    err, av, total = validar(datos, prog, proy)
    if a.xlsx:
        err += validar_xlsx(a.xlsx, a.plantilla)
    for e in err:
        print("ERROR:", e)
    for w in av:
        print("AVISO:", w)
    print(f"{len(datos.get('filas', []))} actividades, {total:g} horas. "
          + ("OK" if not err else f"{len(err)} errores"))
    sys.exit(1 if err else 0)
