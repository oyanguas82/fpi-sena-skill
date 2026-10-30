"""Extrae proyectos formativos SENA (PDF de SOFIA Plus) a JSON.

Formatos:
  - GFPI-F-016 «PROYECTO FORMATIVO»: información básica, problema, objetivos, productos, ambiente y la
    planeación (fase → actividad de proyecto → resultado de aprendizaje → competencia).
  - «VERIFICACIÓN DE LA VIABILIDAD DEL PROYECTO FORMATIVO»: solo código y nombre del proyecto y del programa.
No se guardan nombres de personas.

Uso:
  python extraer_proyecto.py archivo.pdf --salida data/proyectos
  python extraer_proyecto.py carpeta_con_pdfs --salida data/proyectos   (lote; crea data/indice_proyectos.json)
Requiere: pdfplumber.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    sys.exit("Instale pdfplumber: pip install pdfplumber")

ENCABEZADO = re.compile(r"^(SERVICIO NACIONAL DE APRENDIZAJE SENA|Sistema Integrado de Gesti[oó]n y Autocontrol|"
                        r"Procedimiento Ejecuci[oó]n de la Formaci[oó]n|PROYECTO FORMATIVO|Modelo de Mejora)$")
CATALOGO = Path(__file__).resolve().parents[1] / "data" / "programas"
PIE = re.compile(r"GFPI-\s*F-016|P[aá]gina \d+ de \d+")
# «593343 - 01 IDENTIFICAR …» (id SOFIA - número) o «568879 - INTERCAMBIAR …» (solo id SOFIA).
RA_RX = re.compile(r"^(\d{5,7})\s*-\s*(?:(\d{1,2})(?!\d)\s*-?\s*)?(.*)$", re.S)
COMP_RX = re.compile(r"^(\d{9})\s*-\s*(.*)$", re.S)
ACT_RX = re.compile(r"^(\d{1,2})\s*[.\-–)]\s*(.*)$", re.S)  # «1. DESARROLLAR …», «6- APLICAR …»


def nfc(s):
    return unicodedata.normalize("NFC", (s or "").replace("(cid:9)", " ")).strip()


def una_linea(s):
    return re.sub(r"\s+", " ", nfc(s)).strip()


def texto_documento(pdf):
    """Texto del documento sin encabezados ni pies repetidos."""
    lineas = []
    for p in pdf.pages:
        for l in (p.extract_text() or "").split("\n"):
            l = nfc(l)
            if l and not ENCABEZADO.match(l) and not PIE.search(l):
                lineas.append(l)
    return "\n".join(lineas)


def entre(texto, ini, fin):
    m = re.search(ini + r"(.*?)(?=" + fin + r")", texto, re.S)
    return nfc(m.group(1)) if m else ""


def lista_numerada(bloque):
    items, actual = [], ""
    for l in bloque.split("\n"):
        if re.match(r"^\d{1,2}\s*[.)]\s*\S", l):
            if actual:
                items.append(una_linea(actual))
            actual = re.sub(r"^\d{1,2}\s*[.)]\s*", "", l)
        else:
            actual += " " + l
    if actual.strip():
        items.append(una_linea(actual))
    return items


# ---------------------------------------------------------------- planeación
def palabra(pagina, rx):
    return next((w for w in pagina.extract_words() if re.match(rx, w["text"])), None)


def tramo_planeacion(pdf):
    """[(página, y_desde, y_hasta)] de la tabla de planeación: desde el encabezado «3.1. Fases»
    hasta el título «3.5 Organización del proyecto»."""
    tramo, dentro = [], False
    for p in pdf.pages:
        texto = p.extract_text() or ""
        y0 = 95
        if not dentro:
            if not re.search(r"3\.1\.?\s*Fases", texto):
                continue
            dentro = True
            w = palabra(p, r"^3\.1\.?$")
            y0 = (w["top"] + 2) if w else 95
        fin = re.search(r"3\.5\s*Organizaci", texto)
        w = palabra(p, r"^3\.5$") if fin else None
        tramo.append((p, y0, w["top"] - 1 if w else p.height))
        if fin:
            break
    return tramo


def columnas(tramo):
    """Límites de columna, comunes a todo el documento: las 3 líneas verticales más frecuentes de la tabla."""
    xs = {}
    for p, y0, y1 in tramo:
        for l in p.lines:
            if abs(l["x0"] - l["x1"]) < 1 and l["top"] >= y0 - 15 and l["bottom"] <= y1 + 1 \
                    and 120 < l["x0"] < p.width - 60:
                x = round(l["x0"])
                xs[x] = xs.get(x, 0) + 1
    lim = sorted(sorted(xs, key=lambda x: -xs[x])[:3])
    return lim if len(lim) == 3 else None


def filas(pagina):
    """Recuadros de fila (curvas de ancho completo) bajo el encabezado de página."""
    cajas = [(c["top"], c["bottom"]) for c in pagina.curves
             if c["x1"] - c["x0"] > pagina.width * 0.8 and c["top"] > 95 and c["bottom"] - c["top"] > 8]
    return sorted(set((round(t, 1), round(b, 1)) for t, b in cajas))


def texto_celda(pagina, x0, x1, top, bottom):
    t = pagina.crop((x0, top, x1, bottom)).extract_text() or ""
    return una_linea(t)


def planeacion(pdf, avisos):
    tramo = tramo_planeacion(pdf)
    lim = columnas(tramo) if tramo else None
    if not tramo or not lim:
        avisos.append("No se encontró la tabla de la sección 3. Planeación del proyecto")
        return []
    registros = []
    for p, y0, y1 in tramo:
        for top, bottom in filas(p):
            if top < y0 - 1 or top >= y1:
                continue
            bottom = min(bottom, y1)
            bordes = [0] + lim + [p.width]
            celdas = [texto_celda(p, bordes[i], bordes[i + 1], top, bottom) for i in range(4)]
            if re.search(r"3\.1\.?\s*Fases|3\.4\.?\s*Competencia|neaci[oó]n del proyecto", " ".join(celdas)):
                continue
            if not any(celdas):
                continue
            # El recorte puede arrastrar la última línea de la fila anterior antes del código: se devuelve a ella.
            for i, rx in ((2, r"(?<!\d)\d{5,7}\s*-\s*\S"), (3, r"(?<!\d)\d{9}\s*-")):
                m = re.search(rx, celdas[i])
                if m and m.start() > 0 and registros:
                    clave = ("fase", "actividad", "ra", "competencia")[i]
                    registros[-1][clave] = una_linea(registros[-1][clave] + " " + celdas[i][:m.start()])
                    celdas[i] = celdas[i][m.start():]
            mra = RA_RX.match(celdas[2])
            if not mra and registros:  # fila partida por salto de página: continúa la anterior
                prev = registros[-1]
                for k, v in zip(("fase", "actividad", "ra", "competencia"), celdas):
                    if v:
                        prev[k] = una_linea(prev[k] + " " + v)
                continue
            registros.append(dict(zip(("fase", "actividad", "ra", "competencia"), celdas)))
    return registros


FASES = ["DIAGNÓSTICO", "ANÁLISIS", "PLANEACIÓN", "EJECUCIÓN", "EVALUACIÓN", "ETAPA PRÁCTICA", "ETAPA PRODUCTIVA"]
PREFIJOS_FASE = [("DIAGN", "DIAGNÓSTICO"), ("ANALI", "ANÁLISIS"), ("PLANE", "PLANEACIÓN"), ("EJECU", "EJECUCIÓN"),
                 ("EVAL", "EVALUACIÓN"), ("ETAPA PRACT", "ETAPA PRÁCTICA"), ("ETAPA PROD", "ETAPA PRODUCTIVA")]


def plano(s):
    s = unicodedata.normalize("NFD", s.upper())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def fase_canonica(texto):
    """Normaliza la fase: la celda puede arrastrar texto ajeno («EVALUACIÓN EVALUACIÓN», «… 3.5 ORGANIZACIÓN»),
    numeración («4. EVALAUCIÓN») o errores de digitación."""
    p = re.sub(r"^\d+\s*[.\-–]\s*", "", plano(texto))
    p = re.split(r"\s3\.\d", p)[0].strip()
    for prefijo, fase in PREFIJOS_FASE:
        if p.startswith(prefijo) or (len(prefijo) > 5 and prefijo in p):
            return fase
    return una_linea(re.split(r"\s3\.\d", texto)[0]).upper()


def estructurar(registros, avisos):
    """Agrupa por fase (orden del ciclo del proyecto) y por número de actividad de proyecto."""
    acts = {}
    for r in registros:
        mra, mc, ma = RA_RX.match(r["ra"]), COMP_RX.match(r["competencia"]), ACT_RX.match(r["actividad"])
        if not (mra and mc):
            avisos.append(f"Fila sin RA o competencia reconocible: «{(r['ra'] or r['competencia'])[:60]}»")
            continue
        num = int(ma.group(1)) if ma else None
        nombre = una_linea(ma.group(2) if ma else r["actividad"])
        # Sin número, la actividad se identifica por el inicio de su nombre (el PDF corta algunas celdas).
        act = acts.setdefault(num if num is not None else plano(nombre)[:40],
                              {"numero": num, "codigo": f"AP{num}" if num else None, "nombre": nombre,
                               "fase": fase_canonica(r["fase"]), "resultados": []})
        if len(nombre) > len(act["nombre"]):
            act["nombre"] = nombre
        ra_num, ra_texto = mra.group(2), una_linea(mra.group(3))
        # Variante «27050108903. RENOVAR …»: código de competencia + número de RA pegados al texto.
        pegado = re.match(r"^(\d{9})(\d{2})\s*\.?\s*(.*)$", ra_texto)
        if pegado and pegado.group(1) == mc.group(1):
            ra_num, ra_texto = pegado.group(2), pegado.group(3)
        # Prefijos escritos por el instructor: «RA 2:», «RAP2:», «RAP 01.», «RA1.», «RA4 280301208 …».
        rotulo = re.match(r"^R\.?\s?A\.?P?\s*(\d{1,2})\s*[:.\-–]?\s*(?:\d{9}\s*[:.\-–]?\s*)?(.*)$", ra_texto)
        if rotulo:
            ra_num, ra_texto = ra_num or rotulo.group(1), rotulo.group(2)
        res = {"competencia": mc.group(1), "competencia_texto": una_linea(mc.group(2)),
               "ra": f"{int(ra_num):02d}" if ra_num else None, "ra_id_sofia": mra.group(1), "ra_texto": ra_texto}
        if not any(x["ra_id_sofia"] == res["ra_id_sofia"] for x in act["resultados"]):
            act["resultados"].append(res)
    orden = lambda f: FASES.index(f) if f in FASES else len(FASES)
    sin_numero = [a for a in acts.values() if a["numero"] is None]
    if sin_numero:
        avisos.append("Actividades de proyecto sin numerar en el PDF: AP1, AP2… asignados por fase y orden de aparición")
        usados = {a["numero"] for a in acts.values() if a["numero"]}
        n = 0
        for a in sorted(sin_numero, key=lambda a: orden(a["fase"])):  # sorted es estable: conserva el orden del PDF
            n += 1
            while n in usados:
                n += 1
            a["numero"], a["codigo"] = n, f"AP{n}"
    fases = []
    for a in sorted(acts.values(), key=lambda a: (orden(a["fase"]), a["numero"] or 99)):
        if not fases or fases[-1]["fase"] != a["fase"]:
            fases.append({"fase": a["fase"], "actividades": []})
        fases[-1]["actividades"].append({k: v for k, v in a.items() if k != "fase"})
    return fases


# ---------------------------------------------------------------- documento completo
def valor_campo(pagina, rx_desde, rx_hasta, arriba=0, desde_etiqueta=False):
    """Valor de un campo de la información básica leído por posición: el texto de la columna de valores
    (x ≥ 140) entre la línea de la etiqueta anterior (o la propia) y la etiqueta siguiente."""
    lineas = pagina.extract_text_lines()
    ini = next((l for l in lineas if re.match(rx_desde, l["text"])), None)
    fin = next((l for l in lineas if re.match(rx_hasta, l["text"])), None)
    if not ini or not fin:
        return ""
    y0 = ini["top"] - 6 if desde_etiqueta else ini["bottom"] + 1
    y1 = fin["top"] - arriba
    if y1 <= y0:
        return ""
    return una_linea(pagina.crop((140, y0, pagina.width, y1)).extract_text() or "")


def enlazar_catalogo(doc, carpeta, avisos):
    """Completa número y texto oficial de cada RA con el catálogo curricular (data/programas)."""
    p = doc["proyecto"]
    archivos = sorted(Path(carpeta).glob(f"{p.get('programa_codigo')}_v*.json")) if p.get("programa_codigo") else []
    if p.get("programa_version"):
        archivos.sort(key=lambda f: f.stem != f"{p['programa_codigo']}_v{p['programa_version']}")
    if not archivos:
        avisos.append(f"Programa {p.get('programa_codigo')} no está en el catálogo curricular: RA sin enlazar")
        return
    prog = json.loads(archivos[0].read_text(encoding="utf-8"))
    p["catalogo"] = archivos[0].name
    comps = {c["codigo"]: c for c in prog["competencias"]}
    sin = 0
    for f in doc["fases"]:
        for a in f["actividades"]:
            for r in a["resultados"]:
                c = comps.get(r["competencia"])
                ras = c["resultados"] if c else []
                if c:  # el PDF corta el nombre de la competencia en la celda
                    r["competencia_texto"] = c["denominacion"]
                ra = None
                if r["ra"]:
                    ra = next((x for x in ras if x.get("numero") and int(x["numero"]) == int(r["ra"])), None)
                if ra is None:  # por texto: el del PDF puede estar cortado
                    t = re.sub(r"[^A-Z0-9]", "", plano(r["ra_texto"]))
                    def comun(x):
                        o = re.sub(r"[^A-Z0-9]", "", plano(x["denominacion"]))
                        return next((i for i, (u, v) in enumerate(zip(t, o)) if u != v), min(len(t), len(o)))
                    mejor = max(ras, key=comun, default=None)
                    if mejor and comun(mejor) >= min(25, len(t)):
                        ra = mejor
                        if mejor.get("numero"):
                            r["ra"] = f"{int(mejor['numero']):02d}"
                r["en_catalogo"] = ra is not None
                if ra:
                    r["ra_texto_oficial"] = ra["denominacion"]
                else:
                    sin += 1
    if sin:
        version = f"_v{p.get('programa_version')}" if p.get("programa_version") else ""
        nota = "" if archivos[0].stem.endswith(version) else \
            f" (el proyecto es de la versión {p.get('programa_version')} del programa; el catálogo tiene {archivos[0].stem})"
        avisos.append(f"{sin} resultado(s) de aprendizaje sin correspondencia en el catálogo {archivos[0].name}{nota}")


def extraer_f016(pdf, archivo):
    avisos = []
    t = texto_documento(pdf)
    g = lambda rx: (re.search(rx, t, re.S).group(1).strip() if re.search(rx, t, re.S) else None)
    nombre = valor_campo(pdf.pages[0], r"^1\.1\b", r"^1\.4\b", arriba=6) or \
        entre(t, r"1\.3 Nombre del proyecto:", r"\n1\.4")
    programa = valor_campo(pdf.pages[0], r"^1\.4\b", r"^1\.5\b", desde_etiqueta=True) or \
        entre(t, r"1\.4 Programa de Formaci[oó]n", r"\n1\.5")
    programa = una_linea(re.sub(r"al que da respuesta:|^al\b|que da respuesta:", " ", programa)).strip(" .")
    proyecto = {
        "codigo": g(r"C[oó]digo Proyecto SOFIA:\s*(\d+)"),
        "nombre": una_linea(nombre),
        "programa_codigo": g(r"C[oó]digo del Programa SOFIA:\s*(\d+)"),
        "programa_version": g(r"Versi[oó]n del Programa:\s*(\d+)"),
        "programa": programa,
        "centro": una_linea(g(r"1\.1 Centro de Formaci[oó]n:\s*(.+?)\s*1\.2") or ""),
        "regional": una_linea(g(r"1\.2 Regional:\s*([^\n]+)") or ""),
        "duracion_meses": g(r"\(meses\):?\s*(\d+)") or g(r"ejecuci[oó]n del proyecto\s*(\d+)"),
        "formato": "GFPI-F-016",
        "fuente": archivo,
    }
    if proyecto["duracion_meses"]:
        proyecto["duracion_meses"] = int(proyecto["duracion_meses"])
    for k in ("codigo", "programa_codigo"):
        if not proyecto[k]:
            avisos.append(f"Sin {k.replace('_', ' ')} en el PDF (borrador o proyecto no publicado)")
    impacto = entre(t, r"2\.5\.2 Impacto", r"2\.5\.3")
    doc = {
        "proyecto": proyecto,
        "planteamiento": una_linea(entre(t, r"2\.1 Planteamiento del problema[^\n]*", r"2\.2 Justificaci")),
        "justificacion": una_linea(entre(t, r"2\.2 Justificaci[oó]n del proyecto", r"2\.3 Objetivo general")),
        "objetivo_general": una_linea(entre(t, r"2\.3 Objetivo general", r"2\.4 Objetivos espec")),
        "objetivos_especificos": lista_numerada(entre(t, r"2\.4 Objetivos espec[ií]ficos", r"2\.5 Alcance")),
        "beneficiarios": una_linea(entre(t, r"2\.5\.1 Beneficiarios del proyecto", r"2\.5\.2")),
        "impacto": {k.lower(): una_linea(v) for k, v in
                    re.findall(r"(Social|Econ[oó]mico|Ambiental|Tecnol[oó]gico):\s*(.*?)(?=(?:Social|Econ[oó]mico|Ambiental|Tecnol[oó]gico):|$)",
                               impacto, re.S)},
        "productos": lista_numerada(entre(t, r"2\.5\.4\.? Productos o resultados del proyecto", r"2\.6 Innovaci")),
        "ambiente": una_linea(entre(t, r"3\.6 Descripci[oó]n del ambiente de aprendizaje requerido", r"3\.7")),
    }
    doc["fases"] = estructurar(planeacion(pdf, avisos), avisos)
    n = sum(len(a["resultados"]) for f in doc["fases"] for a in f["actividades"])
    declarados = sum(int(x) for x in re.findall(r"1\.9\.[123] N[uú]mero de resultados[^:]*:\s*(\d+)", t))
    if not n:
        avisos.append("La planeación no tiene resultados de aprendizaje reconocibles")
    elif declarados and n != declarados:
        avisos.append(f"Se extrajeron {n} RA y el proyecto declara {declarados} (1.9.1–1.9.3): revisar la planeación")
    enlazar_catalogo(doc, CATALOGO, avisos)
    doc["advertencias"] = avisos
    return doc


def extraer_viabilidad(pdf, archivo):
    t = "\n".join(nfc(p.extract_text() or "") for p in pdf.pages[:1])
    prog = re.search(r"C[OÓ]DIGO\s*\n(?:.*?\n)?.*?\b(\d{5,6})\s*$", t, re.M)
    m_prog = re.search(r"No existe informaci[oó]n\s+(.+?)\s+(\d{5,6})\s*\n", t) or \
        re.search(r"\n([A-ZÁÉÍÓÚÑ ,.]+?)\s+(\d{5,6})\s*\n", t)
    bloque = entre(t, r"NOMBRE DEL PROYECTO\s+C[OÓ]DIGO", r"EQUIPO EJECUTOR")
    cod = re.search(r"\b(\d{6,8})\b", bloque)
    nombre = una_linea(re.sub(r"\b\d{6,8}\b", " ", bloque))
    avisos = ["Solo verificación de viabilidad: el PDF no trae la planeación (fases, actividades ni RA)"]
    if not cod:
        avisos.append("Sin código de proyecto en el PDF")
    return {"proyecto": {"codigo": cod.group(1) if cod else None, "nombre": nombre,
                         "programa_codigo": m_prog.group(2) if m_prog else (prog.group(1) if prog else None),
                         "programa_version": None, "programa": una_linea(m_prog.group(1)) if m_prog else "",
                         "formato": "Verificación de viabilidad", "fuente": archivo},
            "fases": [], "advertencias": avisos}


def extraer(ruta):
    with pdfplumber.open(ruta) as pdf:
        primera = pdf.pages[0].extract_text() or ""
        if "VIABILIDAD" in primera.upper() and "Código Proyecto SOFIA" not in primera:
            return extraer_viabilidad(pdf, Path(ruta).name)
        return extraer_f016(pdf, Path(ruta).name)


def guardar(doc, carpeta):
    p = doc["proyecto"]
    base = p.get("codigo") or "sin_codigo_" + re.sub(r"\W+", "_", Path(p["fuente"]).stem.lower()).strip("_")
    destino = Path(carpeta) / f"{base}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not doc["fases"]:  # no reemplazar un proyecto completo por su verificación de viabilidad
        previo = json.loads(destino.read_text(encoding="utf-8"))
        if previo.get("fases"):
            return destino
    destino.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    ent = Path(a.entrada)
    pdfs = sorted(ent.glob("*.pdf")) if ent.is_dir() else [ent]
    indice = []
    for f in pdfs:
        try:
            d = extraer(f)
        except Exception as e:  # continuar el lote
            print(f"ERROR {f.name}: {e}")
            continue
        dest = guardar(d, a.salida)
        p = d["proyecto"]
        n_ap = sum(len(x["actividades"]) for x in d["fases"])
        n_ra = sum(len(ac["resultados"]) for x in d["fases"] for ac in x["actividades"])
        print(f"{p.get('codigo')} | prog {p.get('programa_codigo')} | {p.get('nombre', '')[:60]} | "
              f"{len(d['fases'])} fases, {n_ap} AP, {n_ra} RA | {len(d['advertencias'])} avisos → {dest.name}")
        indice.append({"codigo": p.get("codigo"), "nombre": p.get("nombre"), "programa_codigo": p.get("programa_codigo"),
                       "programa_version": p.get("programa_version"), "programa": p.get("programa"),
                       "formato": p.get("formato"), "archivo": "proyectos/" + dest.name, "fuente": f.name,
                       "actividades": n_ap, "resultados": n_ra, "advertencias": len(d["advertencias"])})
    if len(pdfs) > 1:
        unicos = {}
        for i in indice:  # mismo código en dos PDF: queda el que trae la planeación
            if i["archivo"] not in unicos or i["resultados"] > unicos[i["archivo"]]["resultados"]:
                unicos[i["archivo"]] = i
        indice = list(unicos.values())
        out = Path(a.salida).parent / "indice_proyectos.json"
        out.write_text(json.dumps(sorted(indice, key=lambda x: x["programa"] or ""), ensure_ascii=False, indent=1),
                       encoding="utf-8")
        print("Índice:", out)


if __name__ == "__main__":
    main()
