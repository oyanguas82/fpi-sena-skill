"""Consulta el catálogo de estructuras curriculares (solo biblioteca estándar).
Uso:
  python buscar_programa.py --buscar "texto o código"
  python buscar_programa.py --programa 228118 [--version 1] --competencias
  python buscar_programa.py --programa 228118 --competencia 220501096
  python buscar_programa.py --archivo ruta/programa.json --competencias
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def indice():
    p = DATA / "indice.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    out = []
    for f in sorted((DATA / "programas").glob("*.json")):
        prog = json.loads(f.read_text(encoding="utf-8"))["programa"]
        out.append({**{k: prog.get(k) for k in ("codigo", "version", "denominacion", "nivel")},
                    "archivo": "programas/" + f.name})
    return out


def cargar(codigo=None, version=None, archivo=None):
    if archivo:
        return json.loads(Path(archivo).read_text(encoding="utf-8"))
    hits = [p for p in indice() if str(p["codigo"]) == str(codigo)
            and (version is None or str(p.get("version")) == str(version))]
    if not hits:
        sys.exit(f"Programa {codigo} no está en el catálogo. Pida el PDF del diseño curricular.")
    if len(hits) > 1 and version is None:
        print("Varias versiones:", ", ".join(str(h.get("version")) for h in hits), "→ se usa la última.")
    return json.loads((DATA / hits[-1]["archivo"]).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--buscar")
    ap.add_argument("--programa")
    ap.add_argument("--version")
    ap.add_argument("--archivo")
    ap.add_argument("--competencias", action="store_true")
    ap.add_argument("--competencia")
    a = ap.parse_args()
    if a.buscar:
        q = norm(a.buscar).split()
        res = [p for p in indice() if all(t in norm(f"{p['codigo']} {p['denominacion']} {p.get('nivel','')}") for t in q)]
        for p in res[:30]:
            print(f"{p['codigo']} v{p.get('version')} | {p['denominacion']} | {p.get('nivel','')}")
        print(f"{len(res)} resultado(s)")
        return
    data = cargar(a.programa, a.version, a.archivo)
    pr = data["programa"]
    print(f"PROGRAMA {pr['codigo']} v{pr.get('version')} – {pr['denominacion']} ({pr.get('nivel','')})")
    if a.competencias or not a.competencia:
        for c in data["competencias"]:
            print(f"- {c['codigo']} | {c['denominacion']} | {c.get('duracion_horas')} h | {len(c.get('resultados', []))} RA")
        return
    c = next((c for c in data["competencias"] if str(c["codigo"]) == str(a.competencia)), None)
    if not c:
        sys.exit("Competencia no encontrada en el programa.")
    print(json.dumps(c, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
