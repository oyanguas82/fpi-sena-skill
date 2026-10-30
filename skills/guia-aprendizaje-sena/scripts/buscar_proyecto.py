"""Consulta los proyectos formativos (data/proyectos).
Uso:
  python buscar_proyecto.py --buscar "software"            # por código/nombre de proyecto o de programa
  python buscar_proyecto.py --programa 228118               # proyectos de un programa
  python buscar_proyecto.py --proyecto 2480542              # datos, fases y actividades de proyecto (AP)
  python buscar_proyecto.py --proyecto 2480542 --actividad AP2   # RA y competencias de una actividad
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def plano(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def indice():
    return json.loads((DATA / "indice_proyectos.json").read_text(encoding="utf-8"))


def cargar(codigo):
    item = next((i for i in indice() if i["codigo"] == codigo or Path(i["archivo"]).stem == codigo), None)
    if not item:
        sys.exit(f"Proyecto {codigo} no está en el catálogo. Pida el PDF del proyecto formativo.")
    return json.loads((DATA / item["archivo"]).read_text(encoding="utf-8"))


def linea(i):
    estado = "solo viabilidad (sin planeación)" if not i["resultados"] else f"{i['actividades']} AP, {i['resultados']} RA"
    return f"{i['codigo']} | programa {i['programa_codigo']} v{i['programa_version'] or '?'} {i['programa']} | {i['nombre']} | {estado}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--buscar")
    ap.add_argument("--programa")
    ap.add_argument("--proyecto")
    ap.add_argument("--actividad", help="AP2, 2 o parte del nombre")
    a = ap.parse_args()
    if a.buscar or a.programa:
        q = plano(a.buscar or "")
        res = [i for i in indice() if (a.programa and i["programa_codigo"] == a.programa) or
               (q and q in plano(" ".join(str(i[k]) for k in ("codigo", "nombre", "programa_codigo", "programa"))))]
        for i in res:
            print(linea(i))
        print(f"{len(res)} proyecto(s)")
        return
    if not a.proyecto:
        ap.error("indique --buscar, --programa o --proyecto")
    d = cargar(a.proyecto)
    p = d["proyecto"]
    if not a.actividad:
        print(f"PROYECTO {p['codigo']} – {p['nombre']}")
        print(f"Programa {p['programa_codigo']} v{p.get('programa_version')} {p['programa']} | {p.get('centro', '')} – "
              f"{p.get('regional', '')} | {p.get('duracion_meses') or '?'} meses | catálogo: {p.get('catalogo', 'no')}")
        for k in ("objetivo_general", "planteamiento"):
            if d.get(k):
                print(f"\n{k.replace('_', ' ').upper()}: {d[k][:600]}{'…' if len(d[k]) > 600 else ''}")
        if d.get("productos"):
            print("\nPRODUCTOS:\n" + "\n".join(f"  {n}. {x}" for n, x in enumerate(d["productos"], 1)))
        if d.get("ambiente"):
            print(f"\nAMBIENTE: {d['ambiente'][:400]}")
        print("\nFASES Y ACTIVIDADES DE PROYECTO:")
        for f in d["fases"]:
            print(f"  {f['fase']}")
            for x in f["actividades"]:
                comps = sorted({r["competencia"] for r in x["resultados"]})
                print(f"    {x['codigo']}-{x['nombre']} | {len(x['resultados'])} RA de {len(comps)} competencia(s)")
        for w in d.get("advertencias", []):
            print("AVISO:", w)
        return
    q = a.actividad.strip()
    num = re.match(r"^(?:AP)?\s*(\d+)$", q, re.I)
    for f in d["fases"]:
        for x in f["actividades"]:
            if (num and x["numero"] == int(num.group(1))) or (not num and plano(q) in plano(x["nombre"])):
                print(f"{x['codigo']}-{x['nombre']}\nFase: {f['fase']} | Proyecto {p['codigo']} | Programa {p['programa_codigo']}")
                por_comp = {}
                for r in x["resultados"]:
                    por_comp.setdefault((r["competencia"], r["competencia_texto"]), []).append(r)
                for (c, ct), rs in sorted(por_comp.items()):
                    print(f"\n  {c} – {ct}")
                    for r in sorted(rs, key=lambda r: r["ra"] or "99"):
                        texto = r.get("ra_texto_oficial") or r["ra_texto"]
                        marca = "" if r.get("en_catalogo") else "  [no está en el catálogo: verificar texto]"
                        print(f"    {c}-{r['ra'] or '??'}. {texto}{marca}")
                return
    sys.exit(f"No se encontró la actividad «{a.actividad}» en el proyecto {p['codigo']}.")


if __name__ == "__main__":
    main()
