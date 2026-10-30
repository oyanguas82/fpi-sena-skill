"""Diligencia una copia de la plantilla GFPI-F-135 conservando sus componentes.
Uso: python generar_guia.py --datos datos.json --salida guia.docx
Solo requiere la biblioteca estandar de Python.
"""
import argparse
import json
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PENDIENTE = "[Pendiente de información del instructor]"
OBJETIVO = ("El objetivo de estas actividades de aprendizaje es buscar que usted estimado aprendiz, "
            "comprenda, construya, demuestre, aplique y transfiera los conocimientos, procedimientos "
            "y valores apropiados de las competencias pertinentes a su programa de formación.")
CAMPOS = [
    ("descripcion", "Descripción de la actividad: "),
    ("ambiente", "Ambiente requerido: "),
    ("estrategias", "Estrategias o técnicas didácticas activas: "),
    ("materiales", "Materiales de formación: "),
    ("apoyo", "Material de apoyo: "),
    ("evidencias", "Evidencias de aprendizaje: "),
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

def string_list(data, key):
    values = data.get(key, [PENDIENTE])
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError(key + " debe ser una lista de textos.")
    return values or [PENDIENTE]

def generate(data, output):
    if not isinstance(data, dict):
        raise ValueError("Los datos deben ser un objeto JSON.")
    allowed = {"identificacion", "presentacion", "contexto_actividades", "actividades",
               "evidencias", "glosario", "bibliografia", "control_documento", "cambios"}
    if set(data) - allowed:
        raise ValueError("Campos desconocidos: " + ", ".join(sorted(set(data) - allowed)))
    template = Path(__file__).resolve().parents[1] / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
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
            for line in val(value).splitlines():
                body.insertBefore(paragraph_like(sample, line), end)
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
        put(p, label + " " + val(ids.get(key)))
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
        values = []
        for index, activity in enumerate(items, 1):
            if set(activity) - {k for k, label in CAMPOS} - {"titulo"}:
                raise ValueError("Campo de actividad desconocido.")
            if activity.get("titulo"):
                values.append(str(activity["titulo"]))
            elif len(items) > 1:
                values.append("Actividad " + str(index))
            for key, label in CAMPOS:
                if key in {"evidencias", "instrumentos"} and section in {"3.1", "3.2"} and key not in activity:
                    continue
                values.append(label + val(activity.get(key)))
        replace_between(h[section], h[following], values)
    replace_between(h["5."], h["6."], string_list(data, "glosario"))
    replace_between(h["6."], h["7."], string_list(data, "bibliografia"))
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
        sample = existing[1].cloneNode(True)
        for row in existing[1:]:
            table.removeChild(row)
        for values in rows:
            if not isinstance(values, list) or len(values) != count or any(not isinstance(v, str) for v in values):
                raise ValueError(key + ": número de columnas o tipo de texto incorrecto.")
            row = sample.cloneNode(True)
            cells = children(row, "tc")
            for cell, value in zip(cells, (["Autor (es)"] if author else []) + values):
                cellparas = children(cell, "p")
                for extra in cellparas[1:]:
                    cell.removeChild(extra)
                put(cellparas[0], value if value else ("" if key == "cambios" and values[-1].startswith("No aplica:") else PENDIENTE))
            table.appendChild(row)
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
    args = parser.parse_args()
    result = generate(json.loads(args.datos.read_text(encoding="utf-8-sig")), args.salida)
    print(result)
