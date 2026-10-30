"""Extrae la estructura curricular de los PDF de diseño curricular SENA (reporte SOFIA Plus).

Soporta los dos formatos del reporte:
  A) "1. CONTENIDOS CURRICULARES DE LA COMPETENCIA" (conocimientos de conceptos y principios / de proceso)
  B) "4.CONTENIDOS CURRICULARES DE LA COMPETENCIA" (conocimientos de proceso / del saber)

Uso:
  python extraer_estructura.py archivo.pdf --salida data/programas
  python extraer_estructura.py carpeta_con_pdfs --salida data/programas   (lote; crea data/indice.json)
Requiere: pdfplumber.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    sys.exit("Instale pdfplumber: pip install pdfplumber")

NIVELES = ["ESPECIALIZACION TECNOLOGICA", "PROFUNDIZACION TECNICA", "TECNOLOGO", "TECNICO", "AUXILIAR",
           "OPERARIO", "CURSO ESPECIAL"]
STOP = {"Y", "E", "O", "U", "EL", "LA", "LOS", "LAS", "DE", "DEL", "AL", "A", "EN", "CON", "PARA",
        "POR", "SU", "SUS", "QUE", "UN", "UNA", "SEGÚN", "SEGUN", "COMO", "SIN", "ENTRE", "SOBRE"}


def nfc(s):
    return unicodedata.normalize("NFC", s.replace("(cid:9)", " ")).strip()


def plain(s):
    s = unicodedata.normalize("NFD", s.upper())
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


# ---------------------------------------------------------------- lectura de líneas
def leer_lineas(pdf):
    paginas = []
    for i, p in enumerate(pdf.pages):
        ls = []
        for l in p.extract_text_lines(strip=True):
            t = nfc(l["text"])
            if t:
                ls.append({"t": t, "x0": l["x0"], "x1": l["x1"], "top": l["top"], "pag": i + 1,
                           "words": [(w["x0"], nfc(w["text"])) for w in _words(l)]})
        paginas.append(ls)
    # Encabezados repetidos y pies de página
    n = len(paginas)
    freq = Counter(plain(l["t"]) for ls in paginas for l in ls if l["top"] < 140)
    rep = {k for k, v in freq.items() if n >= 3 and v >= max(3, 0.3 * n)}
    out = []
    for ls in paginas:
        body = [l for l in ls if not (l["top"] < 140 and plain(l["t"]) in rep)
                and not re.search(r"P[aá]gina\s+\d+\s+de\s+\d+", l["t"])]
        if body:
            body[0]["inicio_pag"] = True
            body[-1]["fin_pag"] = True
        out.extend(body)
    return out


def _words(line):
    words, cur = [], None
    for c in line["chars"]:
        if c["text"].isspace():
            cur = None
            continue
        if cur and c["x0"] - cur["x1"] < 1.5:
            cur["text"] += c["text"]
            cur["x1"] = c["x1"]
        else:
            cur = {"text": c["text"], "x0": c["x0"], "x1": c["x1"]}
            words.append(cur)
    return words


# ---------------------------------------------------------------- utilidades de items
INF = re.compile(r"^(?:(?:\d{9}-?)?\d{1,2}\s*[-.)]?\s+)?([A-ZÁÉÍÓÚÑ]{4,})(AR|ER|IR)(?:LOS|LAS|LA|LO|SE)?\b")


def es_inf(t):
    m = INF.match(plain(t))
    return bool(m) and (m.group(1) + m.group(2)) not in STOP


def es_nuevo(prev, l, umbral, solo_verbos):
    """Heurística para listas sin viñetas: ¿la línea l inicia un ítem nuevo?"""
    if prev is None:
        return True
    p = prev["t"].rstrip()
    if p.split(" ")[-1].upper() in STOP or p.endswith((",", ";", "(", "-")):
        return False
    if solo_verbos:
        return es_inf(l["t"])
    if p.endswith("."):
        return True
    return prev["x1"] < umbral


def _limpia(t):
    return re.sub(r"^\*\s*", "", re.sub(r"\s+", " ", t)).strip()


def _corta_encabezado(buf, ras):
    """Si el búfer termina en un encabezado 'RESULTADO…:' devuelve (continuación, encabezado)."""
    for k in range(len(buf)):
        cab = _limpia(" ".join(l["t"] for l in buf[k:]))
        if not cab.endswith(":"):
            return buf, None
        pc = plain(cab.rstrip(": "))
        if any(pc[:40] == plain(r)[:40] for r in ras) or (k == len(buf) - 1 or es_inf(buf[k]["t"])) and \
                (not ras or k == 0 or es_inf(buf[k]["t"])):
            return buf[:k], cab.rstrip(": ").strip()
    return buf, None


def agrupar(lines, marcador, umbral, avisos, contexto, verbos=False, ras=()):
    """Une líneas envueltas en ítems. Devuelve [(texto, grupo)] donde grupo es el RA (si el PDF agrupa por RA)."""
    usa_marca = bool(marcador) and any(re.match(marcador, l["t"]) for l in lines)
    solo_verbos = verbos and not usa_marca and lines and \
        sum(es_inf(l["t"]) for l in lines) >= 0.4 * len(lines)
    items, grupo, buf, prev = [], None, [], None

    def flush():
        nonlocal grupo, buf
        if not buf:
            return
        cont, cab = _corta_encabezado(buf, ras)
        if cont:
            txt = " ".join(l["t"] for l in cont)
            if items:
                items[-1][0] += " " + txt
            else:
                avisos.append(f"{contexto}: fragmento sin inicio (texto perdido en el PDF): «{txt[:70]}»")
                items.append(["… " + txt, grupo])
        if cab:
            grupo = cab
        buf = []

    for l in lines:
        t = l["t"]
        if usa_marca:
            if re.match(marcador, t):
                flush()
                items.append([t, grupo])
            else:
                buf.append(l)
        else:
            if es_nuevo(prev, l, umbral, solo_verbos) or not items:
                items.append([t, grupo])
            else:
                items[-1][0] += " " + t
        prev = l
    flush()
    res = []
    for txt, g in items:
        txt = _limpia(txt)
        ultima = txt.rstrip(".,;: ").split(" ")[-1].upper() if txt else ""
        if ultima in STOP:
            avisos.append(f"{contexto}: posible texto truncado: «…{txt[-60:]}»")
        if txt:
            res.append((txt, g))
    return res


def ra_lista(lines, umbral, avisos, ctx):
    items = agrupar(lines, r"^(\d{9}-?)?\d{1,2}\s*[-.)]?\s+\S", umbral, avisos, ctx, verbos=True)
    out = []
    for t, _ in items:
        m = re.match(r"^(?:\d{9}-?)?(\d{1,2})\s*[-.)]?\s+(.*)$", t)
        out.append({"numero": m.group(1) if m else None, "denominacion": (m.group(2) if m else t).strip(),
                    "duracion_horas": None})
    out.sort(key=lambda r: int(r["numero"]) if r["numero"] and r["numero"].isdigit() else 99)
    return out


def contenidos(comp, bloques, marcador, umbral, avisos, ctx):
    """Llena conocimientos y criterios; si el PDF los agrupa por RA, también los asigna a cada RA."""
    ras = [r["denominacion"] for r in comp["resultados"]]
    for clave, sec, verbos in (("conocimientos_saber", "saber", False), ("conocimientos_proceso", "proceso", True),
                               ("criterios_evaluacion", "criterios", False)):
        items = agrupar(bloques.get(sec, []), marcador, umbral, avisos, f"{ctx} {sec}", verbos, ras)
        comp[clave] = [t for t, _ in items]
        for t, g in items:
            if not g:
                continue
            pg = plain(g)[:40]
            ra = next((r for r in comp["resultados"] if plain(r["denominacion"])[:40] == pg), None)
            if ra is None:
                ra = next((r for r in comp["resultados"] if pg[:25] in plain(r["denominacion"])), None)
            if ra is not None:
                ra.setdefault(clave, []).append(t)
    return comp


def secciones(lines, patrones):
    """Divide lines en bloques según patrones [(clave, regex)], en el orden en que aparezcan."""
    idx = []
    for i, l in enumerate(lines):
        p = plain(l["t"])
        for k, rx in patrones:
            if re.match(rx, p):
                idx.append((i, k))
                break
    bloques = {}
    for j, (i, k) in enumerate(idx):
        fin = idx[j + 1][0] if j + 1 < len(idx) else len(lines)
        bloques.setdefault(k, lines[i + 1:fin])
    return bloques


def valor(lines, xmin):
    return nfc(" ".join(w for l in lines for x, w in l["words"] if x >= xmin))


# ---------------------------------------------------------------- formato B
PAT_B = [("norma", r"^4\.1\s"), ("codigo", r"^4\.2\s"), ("nombre", r"^4\.3\s"), ("duracion", r"^4\.4\s"),
         ("ra", r"^4\.5\s"), ("conoc", r"^4\.6\s+CONOCIMIENTOS$"), ("proceso", r"^4\.6\.1\s"),
         ("saber", r"^4\.6\.2\s"), ("criterios", r"^4\.7\s"), ("perfil", r"^4\.8\s")]


def comp_b(lines, umbral, avisos):
    # Las primeras líneas de 4.1 incluyen la etiqueta; el valor arranca donde está el código de 4.2.
    xs = [x for l in lines if re.match(r"^4\.2\s", l["t"]) for x, w in l["words"] if re.fullmatch(r"\d{6,9}", w)]
    xs += [x for l in lines for x, w in l["words"] if re.fullmatch(r"\d{6,9}", w)]
    xval = (min(xs) - 3) if xs else 165
    b = secciones(lines, PAT_B)
    # incluir la línea de etiqueta 4.1 / 4.3 (también contiene valor)
    l41 = [l for l in lines if re.match(r"^4\.1\s", l["t"])]
    l43 = [l for l in lines if re.match(r"^4\.3\s", l["t"])]
    codigo = re.search(r"\d{6,9}", " ".join(l["t"] for l in b.get("codigo", []) +
                                            [l for l in lines if re.match(r"^4\.2\s", l["t"])]))
    codigo = codigo.group(0) if codigo else None
    ctx = f"Competencia {codigo}"
    dur = re.search(r"(\d+)\s*horas", " ".join(l["t"] for l in b.get("duracion", []) +
                                              [l for l in lines if re.match(r"^4\.4\s", l["t"])]), re.I)
    ra_lines = [l for l in b.get("ra", []) if plain(l["t"]) != "DENOMINACION"]
    return {
        "codigo": codigo,
        "denominacion": valor(l41 + b.get("norma", []), xval),
        "nombre_corto": valor(l43 + b.get("nombre", []), xval),
        "duracion_horas": int(dur.group(1)) if dur else None,
        "resultados": ra_lista(ra_lines, umbral, avisos, ctx + " RA"),
    } | {"_b": b}


# ---------------------------------------------------------------- formato A
PAT_A = [("cab", r"^CODIGO:"), ("duracion", r"^DURACION ESTIMADA"), ("ra", r"^2\.\s*RESULTADOS DE APRENDIZAJE"),
         ("conoc", r"^3\.\s*CONOCIMIENTOS$"), ("saber", r"^3\.1\.?\s*CONOCIMIENTOS DE CONCEPTOS"),
         ("proceso", r"^3\.2\.?\s*CONOCIMIENTOS DE PROCESO"), ("criterios", r"^4\.\s*CRITERIOS DE EVALUACION"),
         ("fin", r"^NO SE ENCONTRO INFORMACION")]


def comp_a(lines, umbral, avisos):
    b = secciones(lines, PAT_A)
    cab = [l for l in b.get("cab", []) if not re.match(r"^(LA NCL|VERSION DE|DENOMINACION)$", plain(l["t"]))]
    codigo = ncl = None
    resto = []
    for l in cab:
        m = re.match(r"^(\d{6,9})\s+(\S+)(?:\s+(.*))?$", l["t"])
        if m and not codigo:
            codigo, ncl = m.group(1), m.group(2)
            if m.group(3):
                resto.append(m.group(3))
        else:
            resto.append(l["t"])
    ctx = f"Competencia {codigo}"
    dur_txt = " ".join(l["t"] for l in b.get("duracion", []) + [l for l in lines if "DURACI" in plain(l["t"])])
    dur = re.search(r"(\d+)\s*horas", dur_txt, re.I)
    denom = re.split(r"\s+DURACI[OÓ]N ESTIMADA", " ".join(resto))[0]
    m = True
    ra_lines = [l for l in b.get("ra", []) if plain(l["t"]) != "DENOMINACION"]
    return {
        "codigo": codigo,
        "version_ncl": ncl,
        "denominacion": nfc(denom),
        "duracion_horas": int(dur.group(1)) if dur else None,
        "resultados": ra_lista(ra_lines, umbral, avisos, ctx + " RA"),
    } | {"_b": b}


# ---------------------------------------------------------------- programa
def info_programa(texto, formato, archivo):
    t = texto
    g = lambda rx, f=0: (re.search(rx, t, f).group(1).strip() if re.search(rx, t, f) else None)
    if formato == "B":
        den = g(r"1\.1\s*Denominaci[oó]n\s*(?:del Programa:)?\s*(?:del Programa:)?\s*\n?\s*(.+?)\n\s*1\.2", re.S)
        den = re.sub(r"\s*del Programa:\s*", " ", den or "")
        info = {"codigo": g(r"1\.2\.?\s*C[oó]digo\s+(\d+)"),
                "version": g(r"1\.3\.?\s*Versi[oó]n\s*(?:Programa:)?\s*\n?\s*(\d+)"),
                "denominacion": re.sub(r"\s+", " ", den).strip(" ."),
                "nivel": g(r"1\.7\s*T[ií]tulo o\s*\n?.*?\n?\s*certificado que\s+([A-ZÁÉÍÓÚÑ ]+)\n"),
                "duracion_lectiva_horas": g(r"Etapa Lectiva:\s+(\d+)"),
                "duracion_productiva_horas": g(r"Etapa Productiva:\s+(\d+)")}
    else:
        m = re.search(r"C[OÓ]DIGO:\s+DENOMINACI[OÓ]N DEL PROGRAMA\s*\n\s*\n*\s*(\d+)\s+(.+)", t)
        info = {"codigo": m.group(1) if m else None, "denominacion": m.group(2).strip(" .") if m else None,
                "version": g(r"VERSI[OÓ]N:\s+(\S+)"),
                "nivel": g(r"FORMACI[OÓ]N:\s+([A-ZÁÉÍÓÚÑ ]+?)\s*\n"),
                "duracion_lectiva": g(r"Lectiva.*?\n.*?\n?\s*MÁXIMA\s+(\d+\s*meses)", re.S),
                "duracion_total": g(r"Pr[aá]ctica\s+(\d+\s*meses)")}
    for k in ("duracion_lectiva_horas", "duracion_productiva_horas"):
        if info.get(k):
            info[k] = int(info[k])
    zona = t[t.find("NIVEL DE") if formato == "A" else t.find("1.7"):][:600]
    info["nivel"] = next((n.title() for n in NIVELES if n in plain(zona)), None)
    info["formato_reporte"] = formato
    info["fuente"] = archivo
    return info


def extraer(ruta):
    avisos = []
    with pdfplumber.open(ruta) as pdf:
        texto = "\n".join((p.extract_text(layout=True) or "") for p in pdf.pages[:3])
        lines = leer_lineas(pdf)
    formato = "B" if any(re.match(r"^4\.\s*CONTENIDOS CURRICULARES", plain(l["t"])) for l in lines) else "A"
    rx = r"^4\.\s*CONTENIDOS CURRICULARES" if formato == "B" else r"^1\.\s*CONTENIDOS CURRICULARES"
    x1s = sorted(l["x1"] for l in lines)
    umbral = (x1s[int(len(x1s) * 0.97)] if x1s else 580) - 60
    starts = [i for i, l in enumerate(lines) if re.match(rx, plain(l["t"]))]
    comps = []
    for j, s in enumerate(starts):
        fin = starts[j + 1] if j + 1 < len(starts) else len(lines)
        bloque = lines[s + 1:fin]
        c = comp_b(bloque, umbral, avisos) if formato == "B" else comp_a(bloque, umbral, avisos)
        contenidos(c, c.pop("_b"), r"^\*" if formato == "B" else None, umbral, avisos, f"Competencia {c['codigo']}")
        if c["codigo"] and set(c["codigo"]) == {"9"}:
            c["etapa_productiva"] = True
        for k in ("resultados", "criterios_evaluacion"):
            if not c[k] and not c.get("etapa_productiva"):
                avisos.append(f"Competencia {c['codigo']}: sin {k}")
        comps.append(c)
    prog = info_programa(texto, formato, Path(ruta).name)
    if not prog.get("codigo"):
        avisos.append("No se encontró el código del programa")
    return {"programa": prog, "competencias": comps, "advertencias": avisos}


def guardar(data, carpeta):
    p = data["programa"]
    nombre = f"{p.get('codigo') or 'sin_codigo'}_v{p.get('version') or 'x'}.json"
    destino = Path(carpeta) / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
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
        p = d["programa"]
        n_ra = sum(len(c["resultados"]) for c in d["competencias"])
        print(f"{p.get('codigo')} v{p.get('version')} | {p.get('denominacion')} | {len(d['competencias'])} comp | "
              f"{n_ra} RA | {len(d['advertencias'])} avisos → {dest.name}")
        indice.append({k: p.get(k) for k in ("codigo", "version", "denominacion", "nivel")} |
                      {"archivo": "programas/" + dest.name, "fuente": f.name,
                       "competencias": len(d["competencias"]), "advertencias": len(d["advertencias"])})
    if len(pdfs) > 1:
        indice = list({i["archivo"]: i for i in indice}.values())
        out = Path(a.salida).parent / "indice.json"
        out.write_text(json.dumps(sorted(indice, key=lambda x: x["denominacion"] or ""), ensure_ascii=False,
                                  indent=1), encoding="utf-8")
        print("Índice:", out)


if __name__ == "__main__":
    main()
