"""Ubica la skill núcleo guia-aprendizaje-sena (catálogo curricular y plantilla GFPI-F-135)."""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def carpeta_guia():
    hermana = AQUI.parents[1] / "guia-aprendizaje-sena"
    if (hermana / "scripts" / "generar_instrumentos.py").exists():
        return hermana
    for base in (Path("/mnt"), Path.home(), Path("/")):
        try:
            for p in base.rglob("guia-aprendizaje-sena/scripts/generar_instrumentos.py"):
                return p.parents[1]
        except (PermissionError, OSError):
            continue
    raise SystemExit("ERROR: no se encontró la skill guia-aprendizaje-sena (catálogo y plantilla). Instálela junto a esta.")


def scripts_guia():
    s = carpeta_guia() / "scripts"
    if str(s) not in sys.path:
        sys.path.insert(0, str(s))
    return s


def cargar_programa(ruta=None, codigo_version=None):
    if ruta:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    m = re.match(r"\s*(\d+)\s*(?:v(?:ersi[oó]n)?\.?\s*(\d+))?", str(codigo_version or ""), re.I)
    if not m:
        return None
    progs = carpeta_guia() / "data" / "programas"
    cands = sorted(progs.glob(f"{m.group(1)}_v*.json"))
    if m.group(2):
        cands = [c for c in cands if c.stem == f"{m.group(1)}_v{m.group(2)}"] or cands
    return json.loads(cands[0].read_text(encoding="utf-8")) if cands else None


def cap(s):
    s = str(s).strip()
    return s[:1].upper() + s[1:].lower() if s.isupper() else s


def buscar_ra(prog, codigo):
    """'220501096-01' → (competencia, ra) del catálogo, o (None, None)."""
    m = re.match(r"\s*(\d{9})\s*-\s*(\d{1,2})", str(codigo))
    if not prog or not m:
        return None, None
    for c in prog["competencias"]:
        if str(c["codigo"]) == m.group(1):
            for r in c["resultados"]:
                if str(r["numero"]).zfill(2) == m.group(2).zfill(2):
                    return c, r
            return c, None
    return None, None
