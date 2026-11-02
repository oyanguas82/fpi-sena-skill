"""Escritor mínimo de .xlsx (solo biblioteca estándar): hojas con texto/números, encabezado en negrita,
colores para los juicios, anchos de columna y primera fila inmovilizada."""
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

# Estilos: 0 normal, 1 encabezado, 2 aprobado, 3 no aprobado, 4 por evaluar, 5 título
ESTILO_JUICIO = {"APROBADO": 2, "NO APROBADO": 3, "POR EVALUAR": 4, "A": 2, "D": 3}

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="3"><font><sz val="10"/><name val="Arial"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font><font><b/><sz val="12"/><name val="Arial"/></font></fonts>
<fills count="6"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF39A900"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFFFEB9C"/></patternFill></fill></fills>
<borders count="2"><border/><border><left style="thin"><color rgb="FFA6A6A6"/></left><right style="thin"><color rgb="FFA6A6A6"/></right><top style="thin"><color rgb="FFA6A6A6"/></top><bottom style="thin"><color rgb="FFA6A6A6"/></bottom></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="6">
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>"""


def col(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def celda(ref, v, estilo):
    if v is None or v == "":
        return f'<c r="{ref}" s="{estilo}"/>'
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f'<c r="{ref}" s="{estilo}"><v>{v}</v></c>'
    return f'<c r="{ref}" s="{estilo}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>'


def hoja_xml(filas, anchos=None, titulo=None, colorear=False):
    """filas[0] = encabezado. titulo (opcional) va en la fila 1 y el encabezado en la 3."""
    rows, r0 = [], 1
    if titulo:
        rows.append(f'<row r="1">{celda("A1", titulo, 5)}</row>')
        r0 = 3
    for i, fila in enumerate(filas):
        r = r0 + i
        cs = []
        for j, v in enumerate(fila):
            est = 1 if i == 0 else (ESTILO_JUICIO.get(str(v).upper(), 0) if colorear else 0)
            cs.append(celda(f"{col(j)}{r}", v, est))
        rows.append(f'<row r="{r}">' + "".join(cs) + "</row>")
    anchos = anchos or [18] * (max(len(f) for f in filas) if filas else 1)
    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(anchos))
    freeze = (f'<sheetViews><sheetView workbookViewId="0"><pane xSplit="2" ySplit="{r0}" topLeftCell="C{r0 + 1}" '
              f'activePane="bottomRight" state="frozen"/></sheetView></sheetViews>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"{freeze}<cols>{cols}</cols><sheetData>{''.join(rows)}</sheetData></worksheet>")


def escribir(ruta, hojas):
    """hojas: lista de (nombre, xml)."""
    ct = "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                 for i in range(1, len(hojas) + 1))
    with ZipFile(ruta, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   f"{ct}</Types>")
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        sheets = "".join(f'<sheet name="{escape(n[:31])}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(hojas, 1))
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheets}</sheets></workbook>')
        rels = "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                       for i in range(1, len(hojas) + 1))
        rels += f'<Relationship Id="rId{len(hojas) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   f"{rels}</Relationships>")
        z.writestr("xl/styles.xml", STYLES)
        for i, (_, xml) in enumerate(hojas, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", xml)
    return ruta
