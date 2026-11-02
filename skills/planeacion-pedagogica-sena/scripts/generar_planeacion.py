"""Genera la Planeación Pedagógica SENA (GFPI-F-134 V05, Excel) desde la plantilla oficial.
Uso: python generar_planeacion.py --datos planeacion.json --salida <ruta>.xlsx [--programa <programa.json>] [--plantilla <xlsx>]
- Copia la plantilla (logo, encabezado, pie «GFPI-F-134», hoja «Instrucciones») y llena la hoja «FASE».
- Una fila por resultado de aprendizaje (RA); fase, AP, competencia y los datos de la actividad de
  aprendizaje se combinan verticalmente.
- Textos curriculares (competencia, RA, saberes, criterios) se toman LITERALES del catálogo (--programa
  o el catálogo de la skill guia-aprendizaje-sena); en el JSON solo van los códigos.
Solo biblioteca estándar.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

AQUI = Path(__file__).resolve().parent
NOMBRE_PLANTILLA = "GFPI-F-134 Formato Planeacion Pedagogica.xlsx"
HOJA = "xl/worksheets/sheet2.xml"
PRIMERA = 18  # primera fila de datos de la hoja FASE
COLS = "ABCDEFGHIJKLMNOP"
ANCHOS = dict(zip(COLS, [18, 18, 18.4, 35.4, 35.4, 35.4, 35.4, 25.3, 25.3, 26, 26, 22.4, 11.4, 16, 19.4, 21.2]))
PEND = "[Pendiente de información del instructor]"
CLASIF = {"publica": "A8", "clasificada": "F8", "reservada": "K8"}
CAMPOS_ID = {"fecha", "programa", "modalidad", "codigo_version", "proyecto", "codigo_proyecto",
             "equipo", "regional_centro", "clasificacion"}
CAMPOS_FILA = {"fase", "actividad_proyecto", "competencia", "resultados", "actividad_aprendizaje",
               "horas_directas", "horas_independientes", "evidencia", "estrategias", "ambiente",
               "materiales", "instructores", "observaciones", "saberes_conceptos", "saberes_proceso",
               "criterios"}


# ---------- catálogo ----------
def ruta_catalogo():
    """data/ de la skill guia-aprendizaje-sena (hermana en skills/ o en cualquier lugar del disco)."""
    hermana = AQUI.parents[1] / "guia-aprendizaje-sena" / "data"
    if hermana.exists():
        return hermana
    for base in (Path("/mnt"), Path.home(), Path("/")):
        try:
            for p in base.rglob("guia-aprendizaje-sena/data/indice.json"):
                return p.parent
        except (PermissionError, OSError):
            continue
    return None


def cargar_programa(ruta, codigo_version):
    if ruta:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    data = ruta_catalogo()
    m = re.match(r"\s*(\d+)\s*(?:v(?:ersi[oó]n)?\.?\s*(\d+))?", str(codigo_version or ""), re.I)
    if not data or not m:
        raise ValueError("Indique --programa <json del programa> (no se encontró el catálogo curricular).")
    cod, ver = m.group(1), m.group(2)
    cands = sorted((data / "programas").glob(f"{cod}_v*.json"))
    if ver:
        cands = [c for c in cands if c.stem == f"{cod}_v{ver}"] or cands
    if not cands:
        raise ValueError(f"El programa {cod} no está en el catálogo. Indique --programa con el JSON extraído del PDF.")
    return json.loads(cands[0].read_text(encoding="utf-8"))


def cap(s):
    """MAYÚSCULAS del PDF → mayúscula inicial, sin cambiar palabras."""
    s = str(s).strip()
    return s[:1].upper() + s[1:].lower() if s.isupper() else s


def competencia(prog, codigo):
    for c in prog["competencias"]:
        if str(c["codigo"]) == str(codigo).strip():
            return c
    raise ValueError(f"La competencia {codigo} no está en el programa {prog['programa']['codigo']}.")


def resultado(comp, num):
    n = str(num).strip().split("-")[-1].split(".")[0].zfill(2)
    for r in comp["resultados"]:
        if str(r["numero"]).zfill(2) == n:
            return r
    raise ValueError(f"El RA {num} no existe en la competencia {comp['codigo']}.")


def lista(xs):
    return "\n".join("• " + cap(x) for x in xs if str(x).strip())


def texto(v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return PEND
    if isinstance(v, (list, tuple)):
        return "\n".join(str(x) for x in v)
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


# ---------- filas ----------
def expandir(datos, prog):
    """Lista de filas (dict columna→texto) y grupos de combinación vertical."""
    filas, grupos = [], []
    for i, f in enumerate(datos["filas"], 1):
        extra = set(f) - CAMPOS_FILA
        if extra:
            raise ValueError(f"Fila {i}: campos no válidos: {', '.join(sorted(extra))}")
        comp = competencia(prog, f.get("competencia", ""))
        nums = f.get("resultados") or []
        if isinstance(nums, (str, int)):
            nums = [nums]
        if not nums:
            raise ValueError(f"Fila {i}: indique al menos un resultado de aprendizaje.")
        ras = [resultado(comp, n) for n in nums]
        propios = all(r.get("criterios_evaluacion") or r.get("conocimientos_saber") for r in ras)
        inicio = len(filas)
        for r in ras:
            h = f" ({r['duracion_horas']} H)" if r.get("duracion_horas") else ""
            fila = {"A": texto(f.get("fase")), "B": texto(f.get("actividad_proyecto")),
                    "C": f"{comp['codigo']} - {cap(comp['denominacion'])}",
                    "D": f"{comp['codigo']}-{str(r['numero']).zfill(2)}. {cap(r['denominacion'])}{h}"}
            if propios and not any(f.get(k) for k in ("saberes_conceptos", "saberes_proceso", "criterios")):
                fila["E"] = lista(r.get("conocimientos_saber", []))
                fila["F"] = lista(r.get("conocimientos_proceso", []))
                fila["G"] = lista(r.get("criterios_evaluacion", []))
            filas.append(fila)
        # Saberes y criterios de la competencia (o la selección del JSON): una celda combinada por actividad.
        if "E" not in filas[inicio]:
            filas[inicio]["E"] = lista(f.get("saberes_conceptos") or comp.get("conocimientos_saber", []))
            filas[inicio]["F"] = lista(f.get("saberes_proceso") or comp.get("conocimientos_proceso", []))
            filas[inicio]["G"] = lista(f.get("criterios") or comp.get("criterios_evaluacion", []))
            grupos += [(c, inicio, len(filas) - 1) for c in "EFG"]
        d, ind = f.get("horas_directas"), f.get("horas_independientes")
        filas[inicio].update({
            "H": texto(f.get("actividad_aprendizaje")),
            "I": texto(d), "J": texto(ind),
            "K": texto(f.get("evidencia")), "L": texto(f.get("estrategias")),
            "M": texto(f.get("ambiente")), "N": texto(f.get("materiales")),
            "O": texto(f.get("instructores")), "P": str(f.get("observaciones") or "")})
        grupos += [(c, inicio, len(filas) - 1) for c in "HIJKLMNOP"]
    # Fase, AP y competencia iguales y consecutivas se combinan.
    for c in "ABC":
        ini = 0
        for k in range(1, len(filas) + 1):
            if k == len(filas) or filas[k][c] != filas[ini][c] or (c != "A" and filas[k]["A"] != filas[ini]["A"]) \
                    or (c == "C" and filas[k]["B"] != filas[ini]["B"]):
                grupos.append((c, ini, k - 1))
                ini = k
    return filas, [g for g in grupos if g[2] > g[1]]


# ---------- XML ----------
def celda(ref, estilo, valor=None, como_texto=False):
    if valor is None or valor == "":
        return f'<c r="{ref}" s="{estilo}"/>'
    if not como_texto and re.fullmatch(r"\d+(?:\.\d+)?", str(valor)):
        return f'<c r="{ref}" s="{estilo}"><v>{valor}</v></c>'
    return f'<c r="{ref}" s="{estilo}" t="inlineStr"><is><t xml:space="preserve">{escape(str(valor))}</t></is></c>'


def lineas(valor, col, ancho_extra=1):
    if not valor:
        return 1
    cap_ = max(8, int(ANCHOS[col] * ancho_extra))
    return sum(max(1, math.ceil(len(l) / cap_)) for l in str(valor).split("\n"))


def estilos_ajuste(styles):
    """Agrega copias de los estilos de datos con ajuste de texto; devuelve (xml, mapa viejo→nuevo)."""
    m = re.search(r'(<cellXfs count=")(\d+)(">)(.*?)(</cellXfs>)', styles, re.S)
    xfs = re.findall(r"<xf\b[^>]*?(?:/>|>.*?</xf>)", m.group(4), re.S)
    nuevos, mapa = [], {}
    for viejo in (6, 28, 29, 30, 33, 34, 38, 40, 41, 57):
        mx = re.match(r"<xf\b([^>]*?)(?:/>|>(.*)</xf>)$", xfs[viejo], re.S)
        attrs = re.sub(r'\s*applyAlignment="\d"', "", mx.group(1))
        hijos = re.sub(r"<alignment\b[^>]*?(?:/>|>.*?</alignment>)", "", mx.group(2) or "", flags=re.S)
        mapa[viejo] = len(xfs) + len(nuevos)
        nuevos.append(f'<xf{attrs} applyAlignment="1"><alignment vertical="top" wrapText="1"/>{hijos}</xf>')
    total = len(xfs) + len(nuevos)
    xml = styles[:m.start()] + m.group(1) + str(total) + m.group(3) + m.group(4) + "".join(nuevos) + m.group(5) \
        + styles[m.end():]
    return xml, mapa


def poner(hoja, ref, valor, estilo=None):
    """Reemplaza la celda ref (que ya existe en la plantilla) por un valor de texto."""
    rx = re.compile(r'<c r="%s"( s="(\d+)")?[^>]*?(?:/>|>.*?</c>)' % ref, re.S)
    m = rx.search(hoja)
    if not m:
        raise ValueError(f"La plantilla no tiene la celda {ref}.")
    s = estilo if estilo is not None else (m.group(2) or "0")
    return hoja[:m.start()] + celda(ref, s, valor, como_texto=True) + hoja[m.end():]


def ruta_plantilla(plantilla=None):
    if plantilla:
        return Path(plantilla)
    en_assets = AQUI.parent / "assets" / NOMBRE_PLANTILLA
    if en_assets.exists():
        return en_assets
    try:
        sys.path.insert(0, str(AQUI))
        from plantilla_f134 import ruta_plantilla as _incrustada
        return _incrustada()
    except ImportError:
        return en_assets


def generar(datos, salida, programa=None, plantilla_ruta=None):
    if not isinstance(datos, dict) or set(datos) - {"identificacion", "filas"}:
        raise ValueError("El JSON solo admite «identificacion» y «filas».")
    ident = datos.get("identificacion") or {}
    if set(ident) - CAMPOS_ID:
        raise ValueError("Campos de identificación no válidos: " + ", ".join(sorted(set(ident) - CAMPOS_ID)))
    if not datos.get("filas"):
        raise ValueError("«filas» debe tener al menos una actividad de aprendizaje.")
    prog = cargar_programa(programa, ident.get("codigo_version"))
    filas, grupos = expandir(datos, prog)

    plantilla = ruta_plantilla(plantilla_ruta)
    if not plantilla.exists():
        raise ValueError("No se encontró la plantilla GFPI-F-134. Indique --plantilla.")
    salida = Path(salida).resolve()
    if salida == plantilla.resolve():
        raise ValueError("No sobrescriba la plantilla.")
    with ZipFile(plantilla) as z:
        entradas = [(i, z.read(i.filename)) for i in z.infolist()]
    partes = dict((i.filename, b) for i, b in entradas)
    styles, mapa = estilos_ajuste(partes["xl/styles.xml"].decode("utf-8"))
    hoja = partes[HOJA].decode("utf-8")

    # Encabezado
    p = prog["programa"]
    cv = ident.get("codigo_version") or f"{p['codigo']} V{p.get('version', '')}"
    valores = {"E9": ident.get("fecha"), "E10": ident.get("programa") or cap(p["denominacion"]),
               "E11": ident.get("modalidad"), "E12": cv,
               "E13": ident.get("proyecto"), "E14": ident.get("codigo_proyecto")}
    for ref, v in valores.items():
        hoja = poner(hoja, ref, texto(v), mapa[38] if ref != "E9" else mapa[57])
    equipo = ident.get("equipo")
    hoja = poner(hoja, "E15", "Nombres y Apellidos:\n" + texto(equipo), mapa[40])
    hoja = poner(hoja, "K15", "Regional y Centro de formación:\n" + texto(ident.get("regional_centro")), mapa[41])
    clas = (ident.get("clasificacion") or "publica").lower().replace("ú", "u")
    if clas not in CLASIF:
        raise ValueError("clasificacion: publica, clasificada o reservada.")
    etiqueta = {"publica": "Pública", "clasificada": "Pública Clasificada", "reservada": "Pública Reservada"}[clas]
    hoja = poner(hoja, CLASIF[clas], f"{etiqueta}   X")

    # Filas de datos
    xml_filas = []
    for k, f in enumerate(filas):
        r = PRIMERA + k
        ultima = k == len(filas) - 1
        izq, med, der = (mapa[30], mapa[33], mapa[34]) if ultima else (mapa[28], mapa[6], mapa[29])
        altura = 0
        celdas = []
        for c in COLS:
            v = f.get(c)
            celdas.append(celda(f"{c}{r}", izq if c == "A" else der if c == "P" else med, v))
            # La altura se reparte entre las filas combinadas.
            g = next((g for g in grupos if g[0] == c and g[1] == r - PRIMERA), None)
            n = lineas(v, c, 1.25 if c == "M" else 1) / ((g[2] - g[1] + 1) if g else 1)
            altura = max(altura, n)
        ht = min(409, max(30, round(altura * 13.8 + 6, 1)))
        xml_filas.append(f'<row r="{r}" spans="1:16" ht="{ht}" customHeight="1">' + "".join(celdas) + "</row>")
    hoja = re.sub(r'<row r="(1[89]|2\d)".*?</row>', "", hoja, flags=re.S)
    hoja = hoja.replace("</sheetData>", "".join(xml_filas) + "</sheetData>")
    ult = PRIMERA + len(filas) - 1
    hoja = re.sub(r'<dimension ref="[^"]+"/>', f'<dimension ref="A1:Y{max(ult, 29)}"/>', hoja)
    hoja = re.sub(r'topLeftCell="[A-Z]+\d+"', 'topLeftCell="A1"', hoja)
    merges = re.findall(r'<mergeCell ref="[^"]+"/>', hoja)
    merges += [f'<mergeCell ref="{c}{PRIMERA + a}:{c}{PRIMERA + b}"/>' for c, a, b in grupos]
    hoja = re.sub(r"<mergeCells count=\"\d+\">.*?</mergeCells>",
                  f'<mergeCells count="{len(merges)}">' + "".join(merges) + "</mergeCells>", hoja, flags=re.S)

    cambiados = {HOJA: hoja.encode("utf-8"), "xl/styles.xml": styles.encode("utf-8")}
    for c in cambiados.values():
        minidom.parseString(c)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(salida, "w", ZIP_DEFLATED) as z:
        for info, contenido in entradas:
            z.writestr(info, cambiados.get(info.filename, contenido))
    with ZipFile(salida) as z:
        if z.testzip() is not None:
            raise ValueError("El Excel no pasó la comprobación ZIP.")
    return salida


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    ap.add_argument("--programa", type=Path, help="JSON del programa (por defecto, el catálogo de guia-aprendizaje-sena)")
    ap.add_argument("--plantilla", type=Path, help="Plantilla GFPI-F-134 (por defecto, assets/)")
    a = ap.parse_args()
    try:
        print(generar(json.loads(a.datos.read_text(encoding="utf-8-sig")), a.salida, a.programa, a.plantilla))
    except ValueError as e:
        raise SystemExit("ERROR: " + str(e))
