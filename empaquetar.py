"""Empaqueta la skill para Claude (.skill) y el plugin para ChatGPT (.zip).
Uso: python empaquetar.py [--salida ../entregables]
Solo biblioteca estándar.
"""
import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

RAIZ = Path(__file__).resolve().parent
SKILL = RAIZ / "skills" / "guia-aprendizaje-sena"
IGNORAR = {"__pycache__", ".DS_Store", "Thumbs.db"}


def archivos(carpeta):
    for f in sorted(carpeta.rglob("*")):
        if f.is_file() and not IGNORAR & set(f.parts) and f.suffix != ".pyc":
            yield f


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path, default=RAIZ.parent / "entregables")
    salida = ap.parse_args().salida.resolve()
    salida.mkdir(parents=True, exist_ok=True)
    version = json.loads((RAIZ / "plugin.json").read_text(encoding="utf-8"))["version"]

    claude = salida / "guia-aprendizaje-sena.skill"
    with ZipFile(claude, "w", ZIP_DEFLATED) as z:
        for f in archivos(SKILL):
            z.write(f, Path("guia-aprendizaje-sena") / f.relative_to(SKILL))
        for legal in ("LICENSE", "NOTICE.md"):
            z.write(RAIZ / legal, Path("guia-aprendizaje-sena") / legal)

    # La misma skill como .zip, para subirla en ChatGPT (Plugins → Skills → Create → Upload).
    skill_zip = salida / "guia-aprendizaje-sena-skill.zip"
    skill_zip.write_bytes(claude.read_bytes())
    # Copia versionada en el repositorio, descargable desde GitHub (claude.ai y ChatGPT).
    dist = RAIZ / "dist" / "guia-aprendizaje-sena-skill.zip"
    dist.parent.mkdir(exist_ok=True)
    dist.write_bytes(claude.read_bytes())

    chatgpt = salida / "fpi-sena-plugin-chatgpt.zip"
    with ZipFile(chatgpt, "w", ZIP_DEFLATED) as z:
        for f in archivos(SKILL):
            z.write(f, f.relative_to(RAIZ))
        for extra in ["plugin.json", ".codex-plugin/plugin.json", "assets/gpt-icon.png", "LICENSE", "NOTICE.md"]:
            z.write(RAIZ / extra, extra)

    for p in (claude, skill_zip, dist, chatgpt):
        with ZipFile(p) as z:
            assert z.testzip() is None
            print(f"{p}  v{version}  {len(z.namelist())} archivos  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
