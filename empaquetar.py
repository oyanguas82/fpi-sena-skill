"""Empaqueta la skill para Claude (.skill) y el plugin para ChatGPT (.zip).
Antes de empaquetar, regenera scripts/plantilla.py: la plantilla GFPI-F-135 incrustada en base64
para entornos que no exponen archivos binarios a Python (p. ej. ChatGPT).
Uso: python empaquetar.py [--salida ../entregables]
Solo biblioteca estándar.
"""
import argparse
import base64
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

RAIZ = Path(__file__).resolve().parent
SKILL = RAIZ / "skills" / "guia-aprendizaje-sena"
PLANTILLA = SKILL / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
IGNORAR = {"__pycache__", ".DS_Store", "Thumbs.db"}

MODULO = '''"""Plantilla GFPI-F-135 V04 incrustada (base64). La genera empaquetar.py: no editar a mano.
Sirve en entornos donde Python no ve assets/ (p. ej. ChatGPT): los generadores la usan si falta el .docx.
"""
import base64
import tempfile
from pathlib import Path

DOCX_B64 = "{b64}"


def ruta_plantilla(plantilla=None):
    """Ruta de la plantilla: la indicada, la de assets/ o una copia reconstruida desde DOCX_B64."""
    if plantilla:
        return Path(plantilla)
    en_assets = Path(__file__).resolve().parents[1] / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
    if en_assets.exists():
        return en_assets
    copia = Path(tempfile.gettempdir()) / "GFPI-F-135_Formato_Guia_de_Aprendizaje.docx"
    datos = base64.b64decode(DOCX_B64)
    if not copia.exists() or copia.read_bytes() != datos:
        copia.write_bytes(datos)
    return copia
'''


def archivos(carpeta):
    for f in sorted(carpeta.rglob("*")):
        if f.is_file() and not IGNORAR & set(f.parts) and f.suffix != ".pyc":
            yield f


def incrustar_plantilla():
    destino = SKILL / "scripts" / "plantilla.py"
    contenido = MODULO.replace("{b64}", base64.b64encode(PLANTILLA.read_bytes()).decode("ascii"))
    if not destino.exists() or destino.read_text(encoding="utf-8") != contenido:
        destino.write_text(contenido, encoding="utf-8")
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path, default=RAIZ.parent / "entregables")
    salida = ap.parse_args().salida.resolve()
    salida.mkdir(parents=True, exist_ok=True)
    version = json.loads((RAIZ / "plugin.json").read_text(encoding="utf-8"))["version"]
    incrustar_plantilla()

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

    # El plugin para ChatGPT («Complementos» / Plugins) también va en dist/, descargable desde GitHub.
    dist_plugin = RAIZ / "dist" / "fpi-sena-plugin-chatgpt.zip"
    dist_plugin.write_bytes(chatgpt.read_bytes())

    for p in (claude, skill_zip, dist, chatgpt, dist_plugin):
        with ZipFile(p) as z:
            assert z.testzip() is None
            print(f"{p}  v{version}  {len(z.namelist())} archivos  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
