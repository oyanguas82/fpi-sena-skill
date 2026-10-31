"""Diligencia una copia de la plantilla GFPI-F-135 conservando sus componentes.
Uso: python generar_guia.py --datos datos.json --salida guia.docx
Solo requiere la biblioteca estandar de Python.
"""
import argparse
import json
import re
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PENDIENTE = "[Pendiente de información del instructor]"
# Textos introductorios sugeridos por el instructivo del formato GFPI-F-135 V04 (literales).
OBJETIVO = ("El objetivo de estas actividades de aprendizaje es buscar que usted, estimado aprendiz, "
            "comprenda, construya, demuestre, aplique y transfiera los conocimientos, procedimientos "
            "y valores apropiados de las competencias pertinentes a su programa de formación.")
INTRO_MOMENTO = {
    "3.1": ("Estas actividades constituyen el primer momento del acto educativo, esto es «inicio», con el "
            "propósito de fomentar en usted la importancia de que descubra la necesidad sentida de conocimiento, "
            "la cual se va a esclarecer con el desarrollo de las actividades de aprendizaje propuestas."),
    "3.2": ("Estas actividades siguen siendo parte del primer momento del acto educativo «inicio» y dan inicio al "
            "aprendizaje significativo, entendido como un proceso en que se establece una relación sustantiva "
            "entre el objeto de conocimiento por aprender y lo que el aprendiz ya sabe."),
    "3.3": ("Estas actividades son propias del segundo momento del acto educativo «desarrollo» y se enfocan hacia "
            "la construcción integral del conocimiento: conceptos (saber), procedimientos (saber hacer) y valores "
            "(saber ser), cuyo propósito es el de desarrollar capacidades para la elaboración de marcos "
            "conceptuales, la construcción y apropiación de los saberes inherentes a las competencias del "
            "programa de formación."),
    "3.4": ("Las actividades de transferencia del conocimiento corresponden al tercer momento de «cierre» del "
            "proceso formativo y tienen como propósito que el aprendiz ponga en práctica los conocimientos "
            "adquiridos, integrando conceptos, procedimientos y actitudes en contextos reales o simulados, en "
            "coherencia con la situación planteada y los resultados de aprendizaje definidos."),
}
CAMPOS = [
    ("descripcion", "Descripción de la actividad: "),
    ("ambiente", "Ambiente requerido: "),
    ("estrategias", "Estrategias o técnicas didácticas activas: "),
    ("materiales", "Materiales de formación: "),
    ("apoyo", "Material de apoyo: "),
    ("evidencias", "Evidencias de aprendizaje: "),
    ("entrega", "Lineamientos para la entrega: "),
    ("instrumentos", "Instrumentos de evaluación: "),
    ("duracion", "Duración de la actividad (horas): "),
]

def children(node, tag):
    return [c for c in node.childNodes if c.nodeType == c.ELEMENT_NODE
            and c.namespaceURI == W and c.localName == tag]

def text(node):
    return "".join(c.firstChild.data if c.firstChild else ""
                   for c in node.getElementsByTagNameNS(W, "t"))

def val(value):
    if value is None or not str(value).strip():
        return PENDIENTE
    if not isinstance(value, (str, int, float)):
        raise ValueError("Cada campo debe ser texto o un número.")
    return str(value)

def put(paragraph, value):
    # Retiene propiedades del parrafo y del primer segmento de texto.
    runs = paragraph.getElementsByTagNameNS(W, "r")
    props = children(runs[0], "rPr") if runs else []
    props = props[0].cloneNode(True) if props else None
    for c in list(paragraph.childNodes):
        if not (c.nodeType == c.ELEMENT_NODE and c.namespaceURI == W and c.localName == "pPr"):
            paragraph.removeChild(c)
    run = paragraph.ownerDocument.createElementNS(W, "w:r")
    if props:
        run.appendChild(props)
    t = paragraph.ownerDocument.createElementNS(W, "w:t")
    t.setAttribute("xml:space", "preserve")
    t.appendChild(paragraph.ownerDocument.createTextNode("" if value == "" else val(value)))
    run.appendChild(t)
    paragraph.appendChild(run)

def paragraph_like(sample, value):
    p = sample.cloneNode(True)
    # Las listas de orientacion de la plantilla se sustituyen por prosa.
    for props in children(p, "pPr"):
        for numbering in children(props, "numPr"):
            props.removeChild(numbering)
    put(p, value)
    return p


# ---------------------------------------------------------------- formato
# Orden de los hijos de w:pPr y w:rPr exigido por el esquema de Word.
PPR_ORDEN = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
             "sectPr", "pPrChange"]
RPR_ORDEN = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
             "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
             "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText",
             "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def set_child(parent, tag, orden, attrs=None):
    """Crea o reemplaza el hijo w:<tag> respetando el orden del esquema; attrs=None lo elimina."""
    for c in children(parent, tag):
        parent.removeChild(c)
    if attrs is None:
        return None
    el = parent.ownerDocument.createElementNS(W, "w:" + tag)
    for k, v in attrs.items():
        el.setAttribute("w:" + k, str(v))
    pos = orden.index(tag) if tag in orden else len(orden)
    sig = next((c for c in parent.childNodes if c.nodeType == c.ELEMENT_NODE and c.localName in orden
                and orden.index(c.localName) > pos), None)
    parent.insertBefore(el, sig)
    return el


def formato(p, jc=None, before=None, after=None, ind=None, keep=False, line=None):
    """Ajusta alineación, espaciado (en dxa), sangría (izquierda, francesa) y mantener con el siguiente."""
    ppr = children(p, "pPr")
    if ppr:
        ppr = ppr[0]
    else:
        ppr = p.ownerDocument.createElementNS(W, "w:pPr")
        p.insertBefore(ppr, p.firstChild)
    if jc:
        set_child(ppr, "jc", PPR_ORDEN, {"val": jc})
    if before is not None or after is not None or line is not None:
        old = children(ppr, "spacing")
        attrs = {}
        if old:
            for k in ("before", "after", "line", "lineRule"):
                if old[0].getAttribute("w:" + k):
                    attrs[k] = old[0].getAttribute("w:" + k)
        if before is not None:
            attrs["before"] = before
        if after is not None:
            attrs["after"] = after
        if line is not None:
            attrs["line"], attrs["lineRule"] = line, "auto"
        set_child(ppr, "spacing", PPR_ORDEN, attrs)
        set_child(ppr, "contextualSpacing", PPR_ORDEN, None)
    if ind is not None:
        izq, francesa = ind
        attrs = {"left": izq, "firstLine": 0} if not francesa else {"left": izq, "hanging": francesa}
        set_child(ppr, "ind", PPR_ORDEN, attrs)
    if keep:
        set_child(ppr, "keepNext", PPR_ORDEN, {})
    return p


def put_rich(paragraph, segmentos, sz=None):
    """Como put(), pero con varios segmentos [(texto, negrita)]; los saltos de línea van como w:br."""
    runs = paragraph.getElementsByTagNameNS(W, "r")
    base = children(runs[0], "rPr") if runs else []
    if not base:  # párrafo vacío: toma el formato de carácter del propio párrafo
        ppr = children(paragraph, "pPr")
        base = children(ppr[0], "rPr") if ppr else []
    base = base[0] if base else None
    for c in list(paragraph.childNodes):
        if not (c.nodeType == c.ELEMENT_NODE and c.namespaceURI == W and c.localName == "pPr"):
            paragraph.removeChild(c)
    doc = paragraph.ownerDocument
    for texto, negrita in segmentos:
        rpr = base.cloneNode(True) if base else doc.createElementNS(W, "w:rPr")
        for tag in ("b", "bCs"):
            set_child(rpr, tag, RPR_ORDEN, {} if negrita else None)
        if sz:
            for tag in ("sz", "szCs"):
                set_child(rpr, tag, RPR_ORDEN, {"val": sz})
        for i, parte in enumerate(str(texto).split("\n")):
            run = doc.createElementNS(W, "w:r")
            run.appendChild(rpr.cloneNode(True))
            if i:
                run.appendChild(doc.createElementNS(W, "w:br"))
            t = doc.createElementNS(W, "w:t")
            t.setAttribute("xml:space", "preserve")
            t.appendChild(doc.createTextNode(parte))
            run.appendChild(t)
            paragraph.appendChild(run)


def lineas(segmentos):
    """Divide segmentos [(texto, negrita)] en líneas (una por párrafo) según los saltos de línea."""
    out = [[]]
    for texto, negrita in segmentos:
        for i, parte in enumerate(str(texto).split("\n")):
            if i:
                out.append([])
            if parte.strip():
                out[-1].append((parte, negrita))
    return [l for l in out if l] or [[(PENDIENTE, False)]]


def item(segmentos, **fmt):
    """Elemento de contenido: segmentos [(texto, negrita)] más formato de párrafo."""
    return {"segs": segmentos, "fmt": fmt}


def texto_cuerpo(valor):
    return item([(val(valor), False)], jc="both", after=120, ind=(0, 0))


# Códigos oficiales: GA1-220501092-AA1, GA1-220501092-AA1-EV01, IE-GA1-220501092-AA1-EV01.
CODIGO_RX = re.compile(r"(?:IE\s*-\s*)?GA\s*\d+\s*-\s*\d{9}\s*-\s*AA\s*\d+(?:\s*-\s*EV\s*\d{1,2})?", re.I)
# Encabezados de bloque en la identificación («Técnicas:», «Claves:», «Técnico: 248 horas»).
BLOQUE_RX = re.compile(r"^(T[ée]cnic[oa]s?|Claves?|Transversales?)\s*:", re.I)


def rico(texto, etiquetas=False, base=False):
    """Segmentos [(texto, negrita)] con los códigos oficiales en negrita.
    etiquetas=True pone en negrita el rótulo inicial de cada línea («Formato: …»)."""
    out = []
    for i, linea in enumerate(str(texto).split("\n")):
        pre = "\n" if i else ""
        m = re.match(r"^([^:\n]{2,40}:)(\s*)(.*)$", linea) if etiquetas else None
        if m and not CODIGO_RX.match(m.group(1)):
            out.append((pre + m.group(1) + m.group(2), True))
            linea, pre = m.group(3), ""
        pos = 0
        for c in CODIGO_RX.finditer(linea):
            if c.start() > pos or pre:
                out.append((pre + linea[pos:c.start()], base))
                pre = ""
            out.append((c.group(0), True))
            pos = c.end()
        if linea[pos:] or pre:
            out.append((pre + linea[pos:], base))
    return out


def segmentos_identificacion(label, valor):
    """Ítem del apartado 1. Si el valor tiene varias líneas (competencias técnicas y claves, varios RA),
    cada una va en su renglón; «Técnicas:», «Claves:» y los códigos iniciales (220501092-02.) en negrita."""
    texto = val(valor)
    lineas_v = texto.split("\n")
    segs = [(label + " ", True)]
    for i, linea in enumerate(lineas_v):
        pre = "\n" if i or len(lineas_v) > 1 else ""
        m = BLOQUE_RX.match(linea) or re.match(r"^\d{9}(?:\s*-\s*\d{1,2})?\s*[.\-–]?", linea)
        if m and m.end():
            segs += [(pre + linea[:m.end()], True), (linea[m.end():], False)]
        else:
            segs.append((pre + linea, False))
    return segs


def etiqueta_valor(etiqueta, valor, etiquetas=False, **fmt):
    """«Etiqueta: valor» con la etiqueta y los códigos en negrita (valores multilínea → párrafos siguientes)."""
    fmt = {"jc": "both", "after": 80, "ind": (0, 0)} | fmt
    return item([(etiqueta, True)] + rico(val(valor), etiquetas=etiquetas), **fmt)


# Tabla 4: más ancho para evidencia, criterio e instrumento (suma = ancho original 9629).
ANCHOS_EVIDENCIAS = [1300, 1400, 1500, 1650, 1979, 1800]


TBLPR_ORDEN = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
               "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]
TRPR_ORDEN = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight",
              "tblHeader", "tblCellSpacing", "jc", "hidden"]


def anchos_columnas(table, anchos):
    """Fija los anchos (diseño fijo: Word no reajusta por contenido) y repite el encabezado sin partirlo."""
    set_child(children(table, "tblPr")[0], "tblLayout", TBLPR_ORDEN, {"type": "fixed"})
    encabezado = children(table, "tr")[0]
    trpr = children(encabezado, "trPr")
    if not trpr:
        trpr = [table.ownerDocument.createElementNS(W, "w:trPr")]
        encabezado.insertBefore(trpr[0], next((c for c in encabezado.childNodes if c.nodeType == c.ELEMENT_NODE
                                                and c.localName not in ("tblPrEx",)), None))
    set_child(trpr[0], "cantSplit", TRPR_ORDEN, {})
    set_child(trpr[0], "tblHeader", TRPR_ORDEN, {})
    grid = children(table, "tblGrid")[0]
    for col, ancho in zip(children(grid, "gridCol"), anchos):
        col.setAttribute("w:w", str(ancho))
    for row in children(table, "tr"):
        for cell, ancho in zip(children(row, "tc"), anchos):
            for tcpr in children(cell, "tcPr"):
                for tcw in children(tcpr, "tcW"):
                    tcw.setAttribute("w:w", str(ancho))
                    tcw.setAttribute("w:type", "dxa")


def parrafos_celda(valor, col):
    """Párrafos de una celda de la tabla 4: criterios separados por «;», y en la última columna
    «Técnica:» e «Instrumento:» en líneas propias con la etiqueta en negrita."""
    if col == 4:
        return [[(c.strip(), False)] for c in re.split(r"\s*;\s*|\n", valor) if c.strip()]
    if col == 5:
        out = []
        for x in re.split(r"(T[ée]cnica\s*:|Instrumentos?\s*:)", valor):
            if not x.strip():
                continue
            if re.fullmatch(r"T[ée]cnica\s*:|Instrumentos?\s*:", x.strip()):
                out.append([(x.strip() + " ", True)])  # cada etiqueta abre un párrafo
            elif out and len(out[-1]) == 1 and out[-1][0][1]:
                out[-1].extend(rico(x.strip()))
            else:
                out.append(rico(x.strip()))
        return out
    # Evidencias y actividades: una línea por párrafo, códigos oficiales en negrita.
    return [rico(l.strip()) for l in valor.split("\n") if l.strip()] or [[("", False)]]


def llenar_celda(cell, primero, parrafos):
    for i, segs in enumerate(parrafos):
        p = primero if i == 0 else primero.cloneNode(True)
        put_rich(p, segs, sz=20)
        formato(p, jc="left", before=0, after=40 if i < len(parrafos) - 1 else 0, line=240)
        if i:
            cell.appendChild(p)


def termino(entrada):
    """Glosario: «Término: definición\\nImportancia: …» con el término y «Importancia:» en negrita."""
    if ":" in entrada and entrada.index(":") < 60:
        t, d = entrada.split(":", 1)
        m = re.search(r"\s*Importancia\s*:\s*", d)
        d, imp = (d[:m.start()], d[m.end():]) if m else (d, "")
        segs = [(t.strip() + ": ", True), (d.strip(), False)]
        if imp.strip():
            segs += [("\nImportancia: ", True), (imp.strip(), False)]
        return item(segs, jc="both", after=120, ind=(0, 0))
    return texto_cuerpo(entrada)

def string_list(data, key):
    values = data.get(key, [PENDIENTE])
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError(key + " debe ser una lista de textos.")
    return values or [PENDIENTE]

def ruta_plantilla(plantilla=None):
    """Plantilla indicada, la de assets/ o la incrustada en scripts/plantilla.py
    (entornos donde Python no ve assets/, p. ej. ChatGPT)."""
    if plantilla:
        return Path(plantilla)
    en_assets = Path(__file__).resolve().parents[1] / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
    if en_assets.exists():
        return en_assets
    try:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from plantilla import ruta_plantilla as _incrustada
        return _incrustada()
    except ImportError:
        return en_assets


def generate(data, output, plantilla=None):
    if not isinstance(data, dict):
        raise ValueError("Los datos deben ser un objeto JSON.")
    allowed = {"identificacion", "presentacion", "contexto_actividades", "actividades",
               "evidencias", "glosario", "bibliografia", "control_documento", "cambios"}
    if set(data) - allowed:
        raise ValueError("Campos desconocidos: " + ", ".join(sorted(set(data) - allowed)))
    # --plantilla permite usar una copia adjunta (p. ej. en ChatGPT, /mnt/data/…docx).
    template = ruta_plantilla(plantilla)
    if not template.exists():
        raise ValueError("No se encontró la plantilla GFPI-F-135: " + str(template) + ". Indique --plantilla.")
    output = Path(output).resolve()
    if output == template.resolve():
        raise ValueError("No sobrescriba la plantilla empaquetada.")
    with ZipFile(template) as z:
        entries = [(i, z.read(i.filename)) for i in z.infolist()]
    xml = minidom.parseString(dict((i.filename, b) for i, b in entries)["word/document.xml"])
    body = xml.getElementsByTagNameNS(W, "body")[0]
    paras = children(body, "p")
    def heading(prefix):
        return next(p for p in paras if text(p).startswith(prefix))
    h = {k: heading(k) for k in ("1.", "2.", "3. ", "3.1", "3.2", "3.3", "3.4", "4.", "5.", "6.", "7.", "8.")}
    def replace_between(start, end, values):
        between = []
        n = start.nextSibling
        while n is not None and n is not end:
            between.append(n)
            n = n.nextSibling
        samples = [p for p in between if p.nodeType == p.ELEMENT_NODE and p.localName == "p"]
        sample = next((p for p in samples if text(p).strip()), samples[0] if samples else paras[0])
        for n in between:
            body.removeChild(n)
        for value in values:
            elem = value if isinstance(value, dict) else texto_cuerpo(value)
            for i, linea in enumerate(lineas(elem["segs"])):
                p = paragraph_like(sample, "")
                put_rich(p, linea)
                fmt = dict(elem["fmt"])
                if i:  # continuación de un valor multilínea: sin espacio extra antes
                    fmt.pop("before", None)
                formato(p, **fmt)
                body.insertBefore(p, end)
    ids = data.get("identificacion", {})
    keys = ["programa", "codigo", "proyecto", "fase", "actividad_proyecto", "competencia", "resultados", "duracion"]
    if not isinstance(ids, dict) or set(ids) - set(keys):
        raise ValueError("Campos de identificación no válidos.")
    p = h["1."].nextSibling
    for key in keys:
        while p is not None and not (p.nodeType == p.ELEMENT_NODE and p.localName == "p"):
            p = p.nextSibling
        if p is None or p is h["2."]:
            raise ValueError("La estructura de identificación no coincide con la plantilla.")
        label = text(p).rstrip()
        put_rich(p, segmentos_identificacion(label, ids.get(key)))
        # Con saltos de línea manuales, justificar estira las palabras: se alinea a la izquierda.
        formato(p, jc="left" if "\n" in val(ids.get(key)) else "both", after=60)
        p = p.nextSibling
    presentation = string_list(data, "presentacion")
    if "presentacion" in data and len(presentation) != 4:
        raise ValueError("La presentación debe contener cuatro párrafos.")
    if "presentacion" not in data:
        presentation = [PENDIENTE] * 4
    replace_between(h["2."], h["3. "], presentation)
    replace_between(h["3. "], h["3.1"], [OBJETIVO, val(data.get("contexto_actividades"))])
    activities = data.get("actividades", {})
    if not isinstance(activities, dict) or set(activities) - {"3.1", "3.2", "3.3", "3.4"}:
        raise ValueError("Momentos de actividades no válidos.")
    for section, following in [("3.1","3.2"), ("3.2","3.3"), ("3.3","3.4"), ("3.4","4.")]:
        items = activities.get(section) or [{}]
        if not isinstance(items, list) or any(not isinstance(a, dict) for a in items):
            raise ValueError("Cada momento requiere una lista de actividades.")
        values = [item([(INTRO_MOMENTO[section], False)], jc="both", after=160, ind=(0, 0))]
        for index, activity in enumerate(items, 1):
            if set(activity) - {k for k, label in CAMPOS} - {"titulo"}:
                raise ValueError("Campo de actividad desconocido.")
            titulo = activity.get("titulo") or ("Actividad " + str(index) if len(items) > 1 else None)
            if titulo:
                values.append(item([(str(titulo), True)], jc="both", before=200 if index > 1 else 120,
                                   after=80, ind=(0, 0), keep=True))
            for key, label in CAMPOS:
                if key in {"evidencias", "instrumentos"} and section in {"3.1", "3.2"} and key not in activity:
                    continue
                if key == "entrega" and key not in activity:  # opcional: solo si el instructor la define
                    continue
                valor = activity.get(key)
                if key == "instrumentos" and isinstance(valor, str):
                    valor = re.sub(r"\s*;\s*", "\n", valor.strip())  # un instrumento por línea
                values.append(etiqueta_valor(label, valor, etiquetas=key == "entrega",
                                             before=160 if not titulo and index > 1 and key == "descripcion" else None))
        replace_between(h[section], h[following], values)
    replace_between(h["5."], h["6."], [termino(g) for g in string_list(data, "glosario")])
    # Referencias APA: sangría francesa de 1,27 cm, alineadas a la izquierda.
    # «Bibliografía» y «Webgrafía» como entradas propias se muestran como subtítulos en negrita.
    replace_between(h["6."], h["7."], [
        item([(r.strip().rstrip(":"), True)], jc="left", before=120, after=80, ind=(0, 0), keep=True)
        if re.fullmatch(r"\s*(Bibliograf[ií]a|Webgraf[ií]a|Cibergraf[ií]a)\s*:?\s*", r, re.I)
        else item([(val(r), False)], jc="left", after=120, ind=(720, 720))
        for r in string_list(data, "bibliografia")])
    # Respiro antes de cada título de apartado.
    for k in ("2.", "3. ", "4.", "5.", "6.", "7.", "8."):
        formato(h[k], before=240, after=120, keep=True)
    for k in ("3.1", "3.2", "3.3", "3.4"):
        formato(h[k], before=200, after=80, keep=True)
    # Títulos de tabla (4, 7, 8): mantener con la tabla, incluidos los párrafos vacíos intermedios,
    # y el encabezado de cada tabla con su primera fila.
    for k in ("4.", "7.", "8."):
        n = h[k].nextSibling
        while n is not None and n.nodeType == n.ELEMENT_NODE and n.localName == "p":
            formato(n, keep=True)
            n = n.nextSibling
    tables = children(body, "tbl")
    if len(tables) != 3:
        raise ValueError("Se esperaban las tres tablas originales.")
    specs = [(tables[0], "evidencias", 6, False),
             (tables[1], "control_documento", 4, True),
             (tables[2], "cambios", 5, True)]
    for table, key, count, author in specs:
        rows = data.get(key, [[PENDIENTE] * count])
        if key == "cambios" and rows == []:
            rows = [["", "", "", "", "No aplica: primera elaboración"]]
        if not isinstance(rows, list):
            raise ValueError(key + " debe ser una matriz.")
        if not rows:
            rows = [[PENDIENTE] * count]
        existing = children(table, "tr")
        if key == "evidencias":
            anchos_columnas(table, ANCHOS_EVIDENCIAS)
            existing = children(table, "tr")
        sample = existing[1].cloneNode(True)
        for row in existing[1:]:
            table.removeChild(row)
        for values in rows:
            if not isinstance(values, list) or len(values) != count or any(not isinstance(v, str) for v in values):
                raise ValueError(key + ": número de columnas o tipo de texto incorrecto.")
            row = sample.cloneNode(True)
            if key == "evidencias":  # una fila de evidencia no se parte entre páginas
                trpr = children(row, "trPr")
                if not trpr:
                    trpr = [row.ownerDocument.createElementNS(W, "w:trPr")]
                    row.insertBefore(trpr[0], children(row, "tc")[0])
                set_child(trpr[0], "cantSplit", TRPR_ORDEN, {})
            cells = children(row, "tc")
            for col, (cell, value) in enumerate(zip(cells, (["Autor (es)"] if author else []) + values)):
                cellparas = children(cell, "p")
                for extra in cellparas[1:]:
                    cell.removeChild(extra)
                if not value:
                    value = "" if key == "cambios" and values[-1].startswith("No aplica:") else PENDIENTE
                if key == "evidencias":
                    llenar_celda(cell, cellparas[0], parrafos_celda(value, col))
                else:
                    put(cellparas[0], value)
                    if not (author and col == 0):
                        formato(cellparas[0], jc="left")
            table.appendChild(row)
        for cp in children(children(table, "tr")[0], "tc"):
            for pp in children(cp, "p"):
                formato(pp, keep=True)
    xml_bytes = xml.toxml(encoding="UTF-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as z:
        for info, content in entries:
            z.writestr(info, xml_bytes if info.filename == "word/document.xml" else content)
    with ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError("El archivo Word no pasó la comprobación ZIP.")
        minidom.parseString(z.read("word/document.xml"))
        for info, content in entries:
            if info.filename != "word/document.xml" and z.read(info.filename) != content:
                raise ValueError("Se alteró un componente de la plantilla: " + info.filename)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument("--plantilla", type=Path, help="Ruta de la plantilla GFPI-F-135 (por defecto, assets/)")
    args = parser.parse_args()
    result = generate(json.loads(args.datos.read_text(encoding="utf-8-sig")), args.salida, args.plantilla)
    print(result)
