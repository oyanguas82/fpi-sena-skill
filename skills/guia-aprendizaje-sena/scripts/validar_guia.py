"""Valida el JSON de una guía contra la estructura curricular del programa.
Uso: python validar_guia.py --datos datos.json --programa programa.json
Comprueba: competencia y RA literales, criterios oficiales, horas, evidencias en 3.3/3.4,
presentación de 4 párrafos y campos pendientes. Solo biblioteca estándar.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    ap.add_argument("--programa")
    a = ap.parse_args()
    d = json.loads(Path(a.datos).read_text(encoding="utf-8-sig"))
    err, adv = [], []
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

    if a.programa:
        p = json.loads(Path(a.programa).read_text(encoding="utf-8"))
        comp_txt = norm(ident.get("competencia", ""))
        comp = next((c for c in p["competencias"] if str(c["codigo"]) in comp_txt
                     or norm(c["denominacion"]) in comp_txt), None)
        if not comp:
            err.append("La competencia no coincide con ninguna del programa.")
        else:
            oficiales = {norm(x) for x in comp.get("criterios_evaluacion", [])}
            for i, f in enumerate(filas, 1):
                partes = [x for x in re.split(r"\s*;\s*|\n", f[4]) if x.strip()] if len(f) > 4 else []
                for crit in partes:
                    if norm(crit) not in oficiales and not any(norm(crit) in o or o in norm(crit) for o in oficiales if len(o) > 20):
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

    for e in err:
        print("ERROR:", e)
    for w in adv:
        print("AVISO:", w)
    print("OK" if not err else f"{len(err)} error(es)")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
