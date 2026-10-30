"""Valida el JSON de una guía (y de sus instrumentos) contra la estructura curricular.
Uso: python validar_guia.py --datos datos.json [--instrumentos instrumentos.json] --programa programa.json [--proyecto proyecto.json]
Guía: competencias (técnicas y claves) y RA literales, criterios oficiales, horas, evidencias en 3.3/3.4,
presentación de 4 párrafos, actividad de proyecto AP<n> y campos pendientes.
Codificación oficial: actividad GA1-<competencia>-AA1; evidencia GA1-<competencia>-AA1-EV01
(EV de dos dígitos, reinicia en cada AA); instrumento IE-GA1-<competencia>-AA1-EV01 <tipo>.
Instrumentos: criterios oficiales, código IE válido, evidencia presente en la tabla 4, número de
indicadores, descriptores de rúbrica y clave del cuestionario. Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PEND = "[Pendiente de información del instructor]"
COD = r"GA\s*(\d+)\s*-\s*(\d{9})\s*-\s*AA\s*(\d+)"
EV_RX = re.compile(COD + r"\s*-\s*EV\s*(\d{1,2})", re.I)
IE_RX = re.compile(r"^IE\s*-\s*" + COD + r"\s*-\s*EV\s*(\d{1,2})\s+(.+)$", re.I)
IE_COD = re.compile(r"IE\s*-\s*" + COD + r"\s*-\s*EV\s*(\d{1,2})", re.I)
AA_TITULO = re.compile(r"^" + COD + r"\s*[:\-]\s*\S", re.I)
TIPO_IE = {"lista_chequeo": "lista de chequeo", "lista_verificacion": "lista de verificacion",
           "rubrica": "rubrica", "cuestionario": "cuestionario"}
EJ_EV = "GA1-220501092-AA1-EV01"
EJ_IE = "IE-GA1-220501092-AA1-EV01 Lista de chequeo"


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def horas(texto):
    """Suma 'X horas directas y Y ...' o devuelve el primer número."""
    t = norm(texto)
    num = r"(\d+(?:\s\d+)?)"
    di = re.search(num + r"\s*(?:horas?\s*)?directas?", t)
    ind = re.search(num + r"\s*(?:horas?\s*)?(?:de\s*)?trabajo\s*independiente|" + num + r"\s*(?:horas?\s*)?independientes?", t)
    if di or ind:
        f = lambda m: float(next(g for g in m.groups() if g).replace(" ", ".")) if m else 0
        return f(di) + f(ind)
    nums = re.findall(r"\d+(?:[.,]\d+)?", str(texto or ""))
    return float(nums[0].replace(",", ".")) if nums else None


def es_oficial(crit, oficiales):
    n = norm(crit)
    # Marcadores de grupo que quedaron en el catálogo («RA 1», «R.A. 2», «240201524_01») no son criterios.
    if re.fullmatch(r"(r ?a ?)?(\d{9} )?\d{1,2}( (y )?\d{1,2})*", n):
        return False
    return n in oficiales or any(n in o or o in n for o in oficiales if len(o) > 20)


def clave(m):
    """(GA, competencia, AA, EV) de un match de EV_RX o IE_COD."""
    return int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))


def cod_ev(k):
    return f"GA{k[0]}-{k[1]}-AA{k[2]}-EV{k[3]:02d}"


def evidencias_en(texto):
    """Códigos de evidencia del texto (sin contar los de instrumentos «IE-…»)."""
    t = str(texto)
    return {clave(m) for m in EV_RX.finditer(t) if not re.search(r"IE\s*-\s*$", t[max(0, m.start() - 6):m.start()], re.I)}


def competencias_guia(p, texto):
    """Competencias del programa citadas en el texto (por código de 9 dígitos o por denominación)."""
    codigos = set(re.findall(r"\b\d{9}\b", str(texto)))
    comps = [c for c in p["competencias"] if str(c["codigo"]) in codigos]
    if not comps:
        t = norm(texto)
        comps = [c for c in p["competencias"] if norm(c["denominacion"]) in t]
    return comps


def limpia_ra(linea):
    """Quita el código «220501092-02.» y las horas «(248 H)» de una línea de RA."""
    r = re.sub(r"^\s*[-•●]?\s*(\d{9}\s*-\s*\d{1,2})?\s*[.\-–:)]?\s*", "", linea)
    return re.sub(r"\(\s*\d+\s*h(oras)?\s*\)\s*\.?\s*$", "", r, flags=re.I).strip()


def validar_instrumentos(ins, guia, prog, err, adv):
    """Revisa el JSON de instrumentos; guia y prog pueden ser None."""
    lista = ins.get("instrumentos", [])
    if not lista:
        err.append("Instrumentos: la lista está vacía.")
    ident = ins.get("identificacion", {})
    comp_txt = ident.get("competencia") or (guia or {}).get("identificacion", {}).get("competencia", "")
    comps = competencias_guia(prog, comp_txt) if prog else []
    if prog and not comps:
        err.append("Instrumentos: la competencia no coincide con ninguna del programa.")
    codigos_comp = {str(c["codigo"]) for c in comps}
    oficiales = {norm(x) for c in comps for x in c.get("criterios_evaluacion", [])}
    filas = (guia or {}).get("evidencias", [])
    mg = re.match(r"^GA\s*(\d+)\b", str(ident.get("guia", "")).strip(), re.I)
    if not mg:
        err.append(f"Instrumentos: «identificacion.guia» debe ser el código de la guía (p. ej. GA1); hay «{ident.get('guia', '')}».")
    vistos = set()
    for inst in lista:
        cod = str(inst.get("codigo", "")).strip()
        m = IE_RX.match(cod)
        if not m:
            err.append(f"Instrumento «{cod[:70]}»: el código debe tener la forma «{EJ_IE}».")
            continue
        k = clave(m)
        ea = cod_ev(k)
        if mg and k[0] != int(mg.group(1)):
            err.append(f"{cod}: el número de guía no coincide con {ident.get('guia')}.")
        if comps and k[1] not in codigos_comp:
            err.append(f"{cod}: la competencia {k[1]} no está en la guía.")
        if len(m.group(4)) != 2:
            adv.append(f"{cod}: use dos dígitos en la evidencia (EV0{m.group(4)}).")
        if inst.get("tipo") in TIPO_IE and norm(m.group(5)) != TIPO_IE[inst["tipo"]]:
            adv.append(f"{cod}: «{m.group(5)}» no corresponde al tipo «{inst['tipo']}».")
        if k in vistos:
            err.append(f"{cod}: código de instrumento repetido.")
        vistos.add(k)
        crits = inst.get("criterios", [])
        if not crits:
            err.append(f"{cod}: sin criterios de evaluación.")
        for c in crits:
            if comps and not es_oficial(c, oficiales):
                err.append(f"{cod}: criterio no oficial → «{c[:80]}»")
        if guia is not None:
            filas_ea = [f for f in filas if len(f) > 3 and k in evidencias_en(f[3])]
            if not filas_ea:
                err.append(f"{cod}: la evidencia {ea} no está en la tabla 4 de la guía.")
            else:
                crit_tabla = " ".join(norm(f[4]) for f in filas_ea if len(f) > 4)
                for c in crits:
                    if norm(c) not in crit_tabla:
                        adv.append(f"{cod}: el criterio «{c[:60]}…» no figura en la fila de {ea} en la tabla 4.")
                if not any(k in {clave(x) for x in IE_COD.finditer(f[5])} for f in filas_ea if len(f) > 5):
                    adv.append(f"{cod}: el instrumento no figura en la columna «Técnica e instrumento» de {ea}.")
        tipo = inst.get("tipo")
        if tipo in ("lista_chequeo", "lista_verificacion"):
            n = len(inst.get("indicadores", []))
            if not 4 <= n <= 8:
                adv.append(f"{cod}: tiene {n} indicadores; se recomiendan entre 4 y 8.")
        elif tipo == "rubrica":
            niveles = inst.get("niveles") or ["", "", "", ""]
            filas_r = inst.get("rubrica", [])
            if not 3 <= len(filas_r) <= 8:
                adv.append(f"{cod}: tiene {len(filas_r)} indicadores; se recomiendan entre 3 y 8.")
            for i, r in enumerate(filas_r, 1):
                if len(r.get("descriptores", [])) != len(niveles):
                    err.append(f"{cod}: el indicador {i} de la rúbrica no tiene un descriptor por nivel.")
        elif tipo == "cuestionario":
            for i, q in enumerate(inst.get("preguntas", []), 1):
                if q.get("opciones") and q.get("respuesta") in (None, ""):
                    adv.append(f"{cod}: la pregunta {i} no tiene respuesta en la clave.")
        else:
            err.append(f"{cod}: tipo no válido «{tipo}».")
    if guia is not None:
        nombrados = {clave(x) for f in filas if len(f) > 5 for x in IE_COD.finditer(f[5])}
        faltan = nombrados - vistos
        if faltan:
            adv.append("Instrumentos de la tabla 4 sin generar: " + ", ".join("IE-" + cod_ev(k) for k in sorted(faltan)))


def validar_guia(d, p, err, adv):
    ident = d.get("identificacion", {})

    pres = d.get("presentacion", [])
    if len(pres) != 4:
        err.append("La presentación debe tener exactamente 4 párrafos.")

    ap = str(ident.get("actividad_proyecto", "")).strip()
    if ap and PEND not in ap and not re.match(r"^AP\s*\d+\s*-", ap, re.I):
        adv.append("La actividad de proyecto debería iniciar con su código: «AP2-Establecer …».")

    act = d.get("actividades", {})
    for m in ("3.1", "3.2", "3.3", "3.4"):
        if not act.get(m):
            err.append(f"Falta el momento {m}.")
    for m in ("3.3", "3.4"):
        for i, x in enumerate(act.get(m, []), 1):
            if not str(x.get("evidencias", "")).strip() or not str(x.get("instrumentos", "")).strip():
                adv.append(f"{m} actividad {i}: sin evidencia o instrumento (verifique si es subactividad no evaluable).")
            elif not str(x.get("entrega", "")).strip():
                adv.append(f"{m} actividad {i}: faltan los lineamientos de entrega (producto, formato, extensión, envío).")
            titulo = str(x.get("titulo", "")).strip()
            if titulo and not AA_TITULO.match(titulo):
                adv.append(f"{m} actividad {i}: el título debería ser «GA1-<competencia>-AA<n>: <nombre de la actividad>».")
            for ie in re.split(r"\s*;\s*|\n", str(x.get("instrumentos", ""))):
                if ie.strip() and PEND not in ie and not IE_RX.match(ie.strip().rstrip(".")):
                    adv.append(f"{m} actividad {i}: instrumento «{ie[:50]}» sin la forma «{EJ_IE}».")
    texto = json.dumps(d, ensure_ascii=False)
    if re.search(r"\bEA\d+|\bAA\d+\s+-\s+.+?\s+-\s+EV\d", texto):
        adv.append(f"Hay códigos de una codificación anterior (EA1 o «AA1 - … - EV1»): use «{EJ_EV}».")
    total = sum(horas(x.get("duracion")) or 0 for m in act.values() for x in m)
    dur = horas(ident.get("duracion"))
    if dur and total and abs(dur - total) > 0.01:
        err.append(f"Suma de horas de actividades ({total:g}) ≠ duración de la guía ({dur:g}).")

    filas = d.get("evidencias", [])
    if not filas:
        err.append("La tabla de evidencias (apartado 4) está vacía.")
    codigos_tabla = {k for f in filas if len(f) > 3 for k in evidencias_en(f[3])}
    codigos_act = {k for m in act.values() for x in m for k in evidencias_en(x.get("evidencias", ""))}
    if codigos_act - codigos_tabla:
        err.append("Evidencias en actividades que no están en la tabla 4: "
                   + ", ".join(cod_ev(k) for k in sorted(codigos_act - codigos_tabla)))
    if filas and not codigos_tabla:
        err.append(f"La tabla 4 no tiene evidencias codificadas («{EJ_EV}»).")
    if len({k[0] for k in codigos_tabla}) > 1:
        adv.append("Las evidencias usan más de un número de guía (GA).")
    for grupo in sorted({k[:3] for k in codigos_tabla}):
        evs = sorted(k[3] for k in codigos_tabla if k[:3] == grupo)
        if evs != list(range(1, len(evs) + 1)):
            adv.append(f"GA{grupo[0]}-{grupo[1]}-AA{grupo[2]}: las evidencias deben numerarse EV01, EV02… (hay {evs}).")
    if re.search(r"-\s*EV\s*[1-9](?!\d)", texto):
        adv.append("Use dos dígitos en las evidencias: EV01, EV02…")

    if p:
        comps = competencias_guia(p, ident.get("competencia", ""))
        if not comps:
            err.append("La competencia no coincide con ninguna del programa.")
        else:
            codigos_comp = {str(c["codigo"]) for c in comps}
            fuera = {k[1] for k in codigos_tabla | codigos_act} - codigos_comp
            if fuera:
                err.append("Evidencias de competencias que no están en la identificación: " + ", ".join(sorted(fuera)))
            oficiales = {norm(x) for c in comps for x in c.get("criterios_evaluacion", [])}
            for i, f in enumerate(filas, 1):
                partes = [x for x in re.split(r"\s*;\s*|\n", f[4]) if x.strip()] if len(f) > 4 else []
                for crit in partes:
                    if not es_oficial(crit, oficiales):
                        err.append(f"Fila {i} de evidencias: criterio no oficial → «{crit[:80]}»")
            ra_of = {norm(r["denominacion"]) for c in comps for r in c.get("resultados", [])}
            for r in str(ident.get("resultados", "")).splitlines():
                if re.fullmatch(r"\s*[A-Za-zÁÉÍÓÚáéíóú ]{3,25}:\s*", r):  # encabezados «Técnicos:», «Claves:»
                    continue
                r = limpia_ra(r)
                if r.strip() and norm(r) not in ra_of and not any(norm(r) in o for o in ra_of):
                    err.append(f"RA no literal u oficial → «{r[:80]}»")
            if len(comps) == 1:
                ch = comps[0].get("duracion_horas")
                if ch and dur and dur > ch:
                    err.append(f"Duración de la guía ({dur:g} h) supera la de la competencia ({ch} h).")

    pend = json.dumps(d, ensure_ascii=False).count(PEND)
    if pend:
        adv.append(f"{pend} campo(s) pendiente(s) de información del instructor.")


def validar_proyecto(d, proy, err, adv):
    """Coherencia de la guía con el proyecto formativo (data/proyectos/<código>.json)."""
    ident = d.get("identificacion", {})
    ap_txt = str(ident.get("actividad_proyecto", ""))
    m = re.match(r"^AP\s*(\d+)\s*-?\s*(.*)$", ap_txt.strip(), re.I)
    if not m:
        err.append("Con --proyecto, la actividad de proyecto debe iniciar con su código AP<n>.")
        return
    act, fase = None, None
    for f in proy.get("fases", []):
        for a in f["actividades"]:
            if a["numero"] == int(m.group(1)):
                act, fase = a, f["fase"]
    if act is None:
        err.append(f"La actividad AP{m.group(1)} no existe en el proyecto {proy['proyecto'].get('codigo')}.")
        return
    if m.group(2) and norm(m.group(2))[:30] not in norm(act["nombre"]):
        adv.append(f"AP{m.group(1)} se llama en el proyecto «{act['nombre'][:80]}».")
    if ident.get("fase") and norm(ident["fase"])[:5] != norm(fase)[:5]:
        adv.append(f"AP{m.group(1)} pertenece a la fase {fase} del proyecto; la guía dice «{ident['fase']}».")
    del_ap = {(r["competencia"], r["ra"]) for r in act["resultados"]}
    for c, n in re.findall(r"(\d{9})\s*-\s*(\d{1,2})\b", str(ident.get("resultados", ""))):
        if (c, f"{int(n):02d}") not in del_ap:
            adv.append(f"El RA {c}-{int(n):02d} no está planeado en AP{m.group(1)} del proyecto.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", help="JSON de la guía")
    ap.add_argument("--instrumentos", help="JSON de los instrumentos de evaluación")
    ap.add_argument("--programa")
    ap.add_argument("--proyecto", help="JSON del proyecto formativo (data/proyectos/<código>.json)")
    a = ap.parse_args()
    if not a.datos and not a.instrumentos:
        ap.error("indique --datos, --instrumentos o ambos")
    err, adv = [], []
    prog = json.loads(Path(a.programa).read_text(encoding="utf-8")) if a.programa else None
    guia = json.loads(Path(a.datos).read_text(encoding="utf-8-sig")) if a.datos else None
    if a.instrumentos:
        ins = json.loads(Path(a.instrumentos).read_text(encoding="utf-8-sig"))
        validar_instrumentos(ins, guia, prog, err, adv)
        pend = json.dumps(ins, ensure_ascii=False).count(PEND)
        if pend:
            adv.append(f"Instrumentos: {pend} campo(s) pendiente(s).")
    if guia is not None:
        validar_guia(guia, prog, err, adv)
        if a.proyecto:
            validar_proyecto(guia, json.loads(Path(a.proyecto).read_text(encoding="utf-8")), err, adv)
    for e in err:
        print("ERROR:", e)
    for w in adv:
        print("AVISO:", w)
    print("OK" if not err else f"{len(err)} error(es)")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
