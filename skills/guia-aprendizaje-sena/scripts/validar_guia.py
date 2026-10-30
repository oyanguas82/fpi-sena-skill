"""Valida el JSON de una guía (y de sus instrumentos) contra la estructura curricular.
Uso: python validar_guia.py --datos datos.json [--instrumentos instrumentos.json] --programa programa.json
Guía: competencia y RA literales, criterios oficiales, horas, evidencias en 3.3/3.4,
presentación de 4 párrafos y campos pendientes.
Instrumentos: criterios oficiales, código EA presente en la tabla 4, número de indicadores,
descriptores de rúbrica y clave del cuestionario. Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PEND = "[Pendiente de información del instructor]"


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
    return n in oficiales or any(n in o or o in n for o in oficiales if len(o) > 20)


def buscar_competencia(p, texto):
    t = norm(texto)
    return next((c for c in p["competencias"] if str(c["codigo"]) in t
                 or norm(c["denominacion"]) in t), None)


def validar_instrumentos(ins, guia, prog, err, adv):
    """Revisa el JSON de instrumentos; guia y prog pueden ser None."""
    lista = ins.get("instrumentos", [])
    if not lista:
        err.append("Instrumentos: la lista está vacía.")
    comp_txt = ins.get("identificacion", {}).get("competencia") or (guia or {}).get("identificacion", {}).get("competencia", "")
    comp = buscar_competencia(prog, comp_txt) if prog else None
    if prog and not comp:
        err.append("Instrumentos: la competencia no coincide con ninguna del programa.")
    oficiales = {norm(x) for x in comp.get("criterios_evaluacion", [])} if comp else set()
    filas = (guia or {}).get("evidencias", [])
    vistos = set()
    for inst in lista:
        cod = str(inst.get("codigo", ""))
        m = re.match(r"(EA\d+)_", cod)
        if not m:
            err.append(f"Instrumento «{cod[:60]}»: el código debe iniciar con EA<n>_ (p. ej. EA1_Lista_Chequeo_Desempeño_<Nombre>).")
            continue
        ea = m.group(1)
        if cod in vistos:
            err.append(f"{cod}: código de instrumento repetido.")
        vistos.add(cod)
        crits = inst.get("criterios", [])
        if not crits:
            err.append(f"{cod}: sin criterios de evaluación.")
        for c in crits:
            if comp and not es_oficial(c, oficiales):
                err.append(f"{cod}: criterio no oficial → «{c[:80]}»")
        if guia is not None:
            filas_ea = [f for f in filas if re.search(rf"\b{ea}\b", " ".join(f))]
            if not filas_ea:
                err.append(f"{cod}: la evidencia {ea} no está en la tabla 4 de la guía.")
            else:
                crit_tabla = " ".join(norm(f[4]) for f in filas_ea if len(f) > 4)
                for c in crits:
                    if norm(c) not in crit_tabla:
                        adv.append(f"{cod}: el criterio «{c[:60]}…» no figura en la fila de {ea} en la tabla 4.")
                if not any(cod in f[5] for f in filas_ea if len(f) > 5):
                    adv.append(f"{cod}: el nombre del instrumento no coincide con la columna «Técnica e instrumento» de {ea}.")
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
        nombrados = {c for f in filas if len(f) > 5 for c in re.findall(r"EA\d+_[^\s;,.]+", f[5])}
        faltan = nombrados - vistos
        if faltan:
            adv.append("Instrumentos de la tabla 4 sin generar: " + ", ".join(sorted(faltan)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", help="JSON de la guía")
    ap.add_argument("--instrumentos", help="JSON de los instrumentos de evaluación")
    ap.add_argument("--programa")
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
    for e in err:
        print("ERROR:", e)
    for w in adv:
        print("AVISO:", w)
    print("OK" if not err else f"{len(err)} error(es)")
    sys.exit(1 if err else 0)


def validar_guia(d, p, err, adv):
    ident = d.get("identificacion", {})

    pres = d.get("presentacion", [])
    if len(pres) != 4:
        err.append("La presentación debe tener exactamente 4 párrafos.")

    act = d.get("actividades", {})
    for m in ("3.1", "3.2", "3.3", "3.4"):
        if not act.get(m):
            err.append(f"Falta el momento {m}.")
    for m in ("3.3", "3.4"):
        for i, x in enumerate(act.get(m, []), 1):
            if not str(x.get("evidencias", "")).strip() or not str(x.get("instrumentos", "")).strip():
                adv.append(f"{m} actividad {i}: sin evidencia o instrumento (verifique si es subactividad no evaluable).")
    total = sum(horas(x.get("duracion")) or 0 for m in act.values() for x in m)
    dur = horas(ident.get("duracion"))
    if dur and total and abs(dur - total) > 0.01:
        err.append(f"Suma de horas de actividades ({total:g}) ≠ duración de la guía ({dur:g}).")

    filas = d.get("evidencias", [])
    if not filas:
        err.append("La tabla de evidencias (apartado 4) está vacía.")
    codigos_tabla = {c for f in filas for c in re.findall(r"EA\d+", " ".join(f))}
    codigos_act = {c for m in act.values() for x in m for c in re.findall(r"EA\d+", str(x.get("evidencias", "")))}
    if codigos_act - codigos_tabla:
        err.append("Evidencias en actividades que no están en la tabla 4: " + ", ".join(sorted(codigos_act - codigos_tabla)))

    if p:
        comp = buscar_competencia(p, ident.get("competencia", ""))
        if not comp:
            err.append("La competencia no coincide con ninguna del programa.")
        else:
            oficiales = {norm(x) for x in comp.get("criterios_evaluacion", [])}
            for i, f in enumerate(filas, 1):
                partes = [x for x in re.split(r"\s*;\s*|\n", f[4]) if x.strip()] if len(f) > 4 else []
                for crit in partes:
                    if not es_oficial(crit, oficiales):
                        err.append(f"Fila {i} de evidencias: criterio no oficial → «{crit[:80]}»")
            ra_of = {norm(r["denominacion"]) for r in comp.get("resultados", [])}
            for r in str(ident.get("resultados", "")).splitlines():
                r = re.sub(r"^\s*[-•\d.)]+\s*", "", r)
                if r.strip() and norm(r) not in ra_of and not any(norm(r) in o for o in ra_of):
                    err.append(f"RA no literal u oficial → «{r[:80]}»")
            ch = comp.get("duracion_horas")
            if ch and dur and dur > ch:
                err.append(f"Duración de la guía ({dur:g} h) supera la de la competencia ({ch} h).")

    pend = json.dumps(d, ensure_ascii=False).count(PEND)
    if pend:
        adv.append(f"{pend} campo(s) pendiente(s) de información del instructor.")


if __name__ == "__main__":
    main()
