"""Genera en Word los instrumentos de evaluación de una guía (anexo).
Uso: python generar_instrumentos.py --datos instrumentos.json --salida instrumentos.docx
Tipos: lista_chequeo, lista_verificacion, rubrica, cuestionario.
Copia logo, encabezado, estilos y márgenes de la plantilla GFPI-F-135 sin modificarla.
Solo requiere la biblioteca estándar de Python.
"""
import argparse
import json
import re
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape
from zipfile import ZipFile

PENDIENTE = "[Pendiente de información del instructor]"
PIE = "Anexo: instrumentos de evaluación – Guía de Aprendizaje GFPI-F-135 V04"
ANCHO = 9639  # ancho útil en dxa (carta, márgenes de la plantilla)
GRIS = "F2F2F2"
GRIS_OSCURO = "D9D9D9"
CASILLA = "☐"

TIPOS = {
    "lista_chequeo": ("Lista de chequeo", "Observación directa",
                      "Observe el desempeño del aprendiz y marque con una X si cumple o no cada indicador. "
                      "Registre en observaciones los aspectos por mejorar."),
    "lista_verificacion": ("Lista de verificación", "Valoración de producto",
                           "Revise el producto entregado y marque con una X si cumple o no cada indicador. "
                           "Registre en observaciones los aspectos por mejorar."),
    "rubrica": ("Rúbrica", "Valoración de desempeño o producto",
                "Para cada indicador, marque el nivel que mejor describe la evidencia y anótelo en la "
                "columna «Nivel logrado»."),
    "cuestionario": ("Cuestionario", "Formulación de preguntas",
                     "Lea cada pregunta y responda. En las preguntas de selección marque una sola opción."),
}
NIVELES = ["Excelente", "Bueno", "Aceptable", "Insuficiente"]
CAMPOS_ID = {"guia", "programa", "codigo", "ficha", "competencia", "resultados", "instructor"}
CAMPOS_INST = {"codigo", "tipo", "evidencia", "actividad", "tecnica", "criterios", "instrucciones",
               "indicadores", "niveles", "rubrica", "preguntas", "aprobacion"}


def val(value, blank=False):
    if value is None or not str(value).strip():
        return "" if blank else PENDIENTE
    if not isinstance(value, (str, int, float)):
        raise ValueError("Cada campo debe ser texto o un número.")
    return str(value)


def run(texto, bold=False, sz=None, color=None):
    props = ""
    if bold:
        props += "<w:b/><w:bCs/>"
    if color:
        props += f'<w:color w:val="{color}"/>'
    if sz:
        props += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
    partes = str(texto).split("\n")
    out = []
    for i, parte in enumerate(partes):
        if i:
            out.append(f"<w:r>{rpr}<w:br/></w:r>")
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
    return "".join(out)


def para(contenido="", jc=None, after=120, keep=False, sz=22, bold=False, brk=False, runs=None, before=0):
    """Párrafo con texto plano (contenido) o con runs XML ya construidos (runs)."""
    ppr = f'<w:spacing w:before="{before}" w:after="{after}" w:line="259" w:lineRule="auto"/>'
    if keep:
        ppr = "<w:keepNext/>" + ppr
    if brk:
        ppr = "<w:pageBreakBefore/>" + ppr
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs if runs is not None else run(contenido, bold=bold, sz=sz)}</w:p>"


def celda(contenido, ancho, shade=None, span=1, bold=False, jc=None, sz=20, alto_vacio=False):
    tcpr = f'<w:tcW w:w="{ancho}" w:type="dxa"/>'
    if span > 1:
        tcpr += f'<w:gridSpan w:val="{span}"/>'
    if shade:
        tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>'
    tcpr += '<w:vAlign w:val="center"/>'
    if isinstance(contenido, str):
        contenido = [contenido]
    ps = "".join(para(c, jc=jc, after=0, sz=sz, bold=bold) for c in contenido) or para("", after=0)
    if alto_vacio:
        ps += "".join(para("", after=0) for _ in range(3))
    return f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{ps}</w:tc>"


def tabla(anchos, filas, encabezado=0):
    bordes = "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="808080"/>'
                     for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{a}"/>' for a in anchos)
    trs = []
    for i, fila in enumerate(filas):
        trpr = "<w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if i < encabezado else "") + "</w:trPr>"
        trs.append(f"<w:tr>{trpr}{''.join(fila)}</w:tr>")
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(anchos)}" w:type="dxa"/><w:tblBorders>{bordes}</w:tblBorders>'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="85" w:type="dxa"/>'
            f'<w:right w:w="85" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
            f"{''.join(trs)}</w:tbl>")


def lista_textos(inst, clave, minimo=1):
    valores = inst.get(clave, [])
    if not isinstance(valores, list) or any(not isinstance(v, str) for v in valores):
        raise ValueError(f"{inst.get('codigo', '?')}: «{clave}» debe ser una lista de textos.")
    return valores if len(valores) >= minimo else [PENDIENTE]


def identificacion(ident, inst, nombre, tecnica):
    filas = [
        ("Guía de aprendizaje", val(ident.get("guia"))),
        ("Programa de formación", " – ".join(x for x in (val(ident.get("codigo"), True), val(ident.get("programa"))) if x)),
        ("Ficha", val(ident.get("ficha"), True)),
        ("Competencia", val(ident.get("competencia"))),
        ("Resultado(s) de aprendizaje", val(ident.get("resultados"))),
        ("Actividad de aprendizaje", val(inst.get("actividad"))),
        ("Evidencia", val(inst.get("evidencia"))),
        ("Técnica", val(inst.get("tecnica") or tecnica)),
        ("Instrumento", val(inst.get("codigo"))),
        ("Instructor(a)", val(ident.get("instructor"))),
        ("Aprendiz(ces)", ""),
        ("Documento de identidad", ""),
        ("Fecha", ""),
    ]
    return tabla([2700, ANCHO - 2700],
                 [[celda(k, 2700, GRIS, bold=True), celda(v, ANCHO - 2700)] for k, v in filas])


def cuerpo_lista(inst):
    a = [500, ANCHO - 500 - 900 - 900 - 2200, 900, 900, 2200]
    filas = [[celda(t, w, GRIS_OSCURO, bold=True, jc="center") for t, w in
              zip(["N°", "Indicador", "Cumple", "No cumple", "Observaciones"], a)]]
    for i, ind in enumerate(lista_textos(inst, "indicadores"), 1):
        filas.append([celda(str(i), a[0], jc="center"), celda(ind, a[1]),
                      celda("", a[2]), celda("", a[3]), celda("", a[4])])
    return tabla(a, filas, encabezado=1)


def cuerpo_rubrica(inst):
    niveles = inst.get("niveles") or NIVELES
    if not isinstance(niveles, list) or not 2 <= len(niveles) <= 5:
        raise ValueError(f"{inst.get('codigo', '?')}: «niveles» debe tener entre 2 y 5 textos.")
    criterios = inst.get("rubrica") or [{}]
    if not isinstance(criterios, list) or any(not isinstance(c, dict) for c in criterios):
        raise ValueError(f"{inst.get('codigo', '?')}: «rubrica» debe ser una lista de objetos.")
    primera, ultima = 2000, 1000
    resto = (ANCHO - primera - ultima) // len(niveles)
    a = [primera] + [resto] * len(niveles) + [ANCHO - primera - ultima - resto * len(niveles) + ultima]
    filas = [[celda("Indicador", a[0], GRIS_OSCURO, bold=True, jc="center")] +
             [celda(n, resto, GRIS_OSCURO, bold=True, jc="center") for n in niveles] +
             [celda("Nivel logrado", a[-1], GRIS_OSCURO, bold=True, jc="center")]]
    for c in criterios:
        desc = c.get("descriptores") or []
        if desc and len(desc) != len(niveles):
            raise ValueError(f"{inst.get('codigo', '?')}: cada indicador necesita un descriptor por nivel.")
        desc = desc or [PENDIENTE] * len(niveles)
        filas.append([celda(val(c.get("indicador")), a[0], GRIS, bold=True, sz=18)] +
                     [celda(val(d), resto, sz=18) for d in desc] + [celda("", a[-1])])
    return tabla(a, filas, encabezado=1)


def letra(i):
    return "abcdefghij"[i]


def cuerpo_cuestionario(inst):
    preguntas = inst.get("preguntas") or [{}]
    if not isinstance(preguntas, list) or any(not isinstance(p, dict) for p in preguntas):
        raise ValueError(f"{inst.get('codigo', '?')}: «preguntas» debe ser una lista de objetos.")
    out, clave = [], []
    for i, p in enumerate(preguntas, 1):
        out.append(para(f"{i}. {val(p.get('enunciado'))}", bold=True, keep=True, after=60))
        opciones = p.get("opciones") or []
        if len(opciones) > 10:
            raise ValueError(f"{inst.get('codigo', '?')}: máximo 10 opciones por pregunta.")
        if opciones:
            for j, o in enumerate(opciones):
                ultima = j == len(opciones) - 1
                out.append(para(f"{CASILLA} {letra(j)}) {val(o)}", after=160 if ultima else 0, keep=not ultima))
        else:
            out.append(para("_" * 85 + "\n" + "_" * 85 + "\n" + "_" * 85, after=160))
        resp = p.get("respuesta")
        if isinstance(resp, int) and opciones and 0 <= resp < len(opciones):
            resp = letra(resp)
        if opciones:
            clave.append(f"{i}. {val(resp)}")
        elif resp:
            clave.append(f"{i}. Pregunta abierta. Respuesta esperada: {val(resp)}")
        else:
            clave.append(f"{i}. Pregunta abierta: valore la respuesta con el criterio de evaluación.")
    return "".join(out), clave


def instrumento(ident, inst, primero):
    if not isinstance(inst, dict) or set(inst) - CAMPOS_INST:
        raise ValueError("Campos de instrumento no válidos: " + ", ".join(sorted(set(inst) - CAMPOS_INST)))
    tipo = inst.get("tipo")
    if tipo not in TIPOS:
        raise ValueError(f"{inst.get('codigo', '?')}: tipo debe ser uno de {', '.join(TIPOS)}.")
    nombre, tecnica, instrucciones = TIPOS[tipo]
    x = [para(val(inst.get("codigo")), jc="center", bold=True, sz=24, after=60, brk=not primero),
         para(nombre.upper(), jc="center", bold=True, sz=22, after=200),
         identificacion(ident, inst, nombre, tecnica),
         para("", after=0),
         para("Criterio(s) de evaluación (estructura curricular)", bold=True, keep=True, after=60)]
    x += [para("• " + c, after=40) for c in lista_textos(inst, "criterios")]
    x += [para("Instrucciones", bold=True, keep=True, after=60, before=120),
          para(val(inst.get("instrucciones") or instrucciones), jc="both")]
    clave = None
    if tipo in ("lista_chequeo", "lista_verificacion"):
        x.append(cuerpo_lista(inst))
    elif tipo == "rubrica":
        x.append(cuerpo_rubrica(inst))
    else:
        preguntas, clave = cuerpo_cuestionario(inst)
        x.append(preguntas)
    x += [para("", after=0),
          para("Criterio de aprobación: " + val(inst.get("aprobacion")), jc="both", keep=True),
          tabla([ANCHO], [[celda("Observaciones y retroalimentación:", ANCHO, bold=True, alto_vacio=True)]]),
          para("", after=0),
          para(runs=run("Juicio de evaluación:   ", bold=True, sz=22) + run(f"{CASILLA} Aprobado     {CASILLA} No aprobado", sz=22),
               keep=True, after=360)]
    m = ANCHO // 2
    x.append(tabla([m, ANCHO - m], [[celda(["", "", "_" * 34, "Firma del instructor(a)"], m, jc="center"),
                                     celda(["", "", "_" * 34, "Firma del aprendiz"], ANCHO - m, jc="center")]]))
    if clave:
        x += [para(f"Clave de respuestas – {val(inst.get('codigo'))}", bold=True, brk=True, after=60),
              para("Uso exclusivo del instructor. Retire esta página antes de aplicar el cuestionario.",
                   after=200, sz=20)]
        x += [para(c, after=40) for c in clave]
    return "".join(x)


def generar(datos, salida):
    if not isinstance(datos, dict) or set(datos) - {"identificacion", "instrumentos"}:
        raise ValueError("El JSON solo admite «identificacion» e «instrumentos».")
    ident = datos.get("identificacion", {})
    if not isinstance(ident, dict) or set(ident) - CAMPOS_ID:
        raise ValueError("Campos de identificación no válidos: " + ", ".join(sorted(set(ident) - CAMPOS_ID)))
    instrumentos = datos.get("instrumentos")
    if not isinstance(instrumentos, list) or not instrumentos:
        raise ValueError("«instrumentos» debe ser una lista con al menos un instrumento.")
    plantilla = Path(__file__).resolve().parents[1] / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
    salida = Path(salida).resolve()
    if salida == plantilla.resolve():
        raise ValueError("No sobrescriba la plantilla empaquetada.")
    with ZipFile(plantilla) as z:
        entradas = [(i, z.read(i.filename)) for i in z.infolist()]
    partes = dict((i.filename, b) for i, b in entradas)
    doc = partes["word/document.xml"].decode("utf-8")
    inicio = doc[:doc.index("<w:body>") + len("<w:body>")]
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S).group(0)
    cuerpo = "".join(instrumento(ident, inst, i == 0) for i, inst in enumerate(instrumentos))
    nuevo_doc = (inicio + cuerpo + sect + "</w:body></w:document>").encode("utf-8")
    pie = partes["word/footer1.xml"].decode("utf-8")
    pie_nuevo, n = re.subn(r"<w:r>\s*<w:t>GFPI-F-</w:t>.*?<w:t>04</w:t></w:r>",
                           run(PIE, sz=18), pie, flags=re.S)
    if n != 1:
        raise ValueError("El pie de página de la plantilla no tiene la estructura esperada.")
    cambiados = {"word/document.xml": nuevo_doc, "word/footer1.xml": pie_nuevo.encode("utf-8")}
    for contenido in cambiados.values():
        minidom.parseString(contenido)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(salida, "w") as z:
        for info, contenido in entradas:
            z.writestr(info, cambiados.get(info.filename, contenido))
    with ZipFile(salida) as z:
        if z.testzip() is not None:
            raise ValueError("El archivo Word no pasó la comprobación ZIP.")
        for info, contenido in entradas:
            if info.filename not in cambiados and z.read(info.filename) != contenido:
                raise ValueError("Se alteró un componente de la plantilla: " + info.filename)
    return salida


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datos", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    a = ap.parse_args()
    try:
        print(generar(json.loads(a.datos.read_text(encoding="utf-8-sig")), a.salida))
    except ValueError as e:
        raise SystemExit("ERROR: " + str(e))
