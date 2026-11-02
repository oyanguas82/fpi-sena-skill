"""Empaqueta cada skill para Claude (.skill / -skill.zip) y el plugin con todas para ChatGPT (.zip).
Antes de empaquetar, regenera scripts/plantilla.py y planeacion-pedagogica-sena/scripts/plantilla_f134.py:
las plantillas GFPI-F-135 y GFPI-F-134 incrustadas en base64
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
SKILLS = RAIZ / "skills"
SKILL = SKILLS / "guia-aprendizaje-sena"
PLANTILLA = SKILL / "assets" / "GFPI-F-135 Formato Guia de Aprendizaje.docx"
PLANEACION = SKILLS / "planeacion-pedagogica-sena"
PLANTILLA_134 = PLANEACION / "assets" / "GFPI-F-134 Formato Planeacion Pedagogica.xlsx"
# Orden de empaquetado: el núcleo primero (las demás skills usan su catálogo y su plantilla).
ORDEN = ["guia-aprendizaje-sena", "planeacion-pedagogica-sena", "instrumentos-evaluacion-sena",
         "juicios-evaluativos-sena", "asistente-fpi-sena"]
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


MODULO_134 = MODULO.replace("Plantilla GFPI-F-135 V04", "Plantilla GFPI-F-134 V05").replace(
    "DOCX_B64", "XLSX_B64").replace("GFPI-F-135 Formato Guia de Aprendizaje.docx", "GFPI-F-134 Formato Planeacion Pedagogica.xlsx").replace(
    "GFPI-F-135_Formato_Guia_de_Aprendizaje.docx", "GFPI-F-134_Formato_Planeacion_Pedagogica.xlsx").replace(
    "falta el .docx", "falta el .xlsx")


def incrustar(destino, modulo, plantilla):
    contenido = modulo.replace("{b64}", base64.b64encode(plantilla.read_bytes()).decode("ascii"))
    if not destino.exists() or destino.read_text(encoding="utf-8") != contenido:
        destino.write_text(contenido, encoding="utf-8")
    return destino


def incrustar_plantilla():
    incrustar(PLANEACION / "scripts" / "plantilla_f134.py", MODULO_134, PLANTILLA_134)
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

    generados = []
    (RAIZ / "dist").mkdir(exist_ok=True)
    for nombre in ORDEN:
        carpeta = SKILLS / nombre
        claude = salida / f"{nombre}.skill"
        with ZipFile(claude, "w", ZIP_DEFLATED) as z:
            for f in archivos(carpeta):
                z.write(f, Path(nombre) / f.relative_to(carpeta))
            for legal in ("LICENSE", "NOTICE.md"):
                z.write(RAIZ / legal, Path(nombre) / legal)
        # La misma skill como .zip (claude.ai › Skills y ChatGPT › Skills) y copia en dist/ para GitHub.
        skill_zip = salida / f"{nombre}-skill.zip"
        skill_zip.write_bytes(claude.read_bytes())
        dist = RAIZ / "dist" / f"{nombre}-skill.zip"
        dist.write_bytes(claude.read_bytes())
        generados += [claude, skill_zip, dist]

    chatgpt = salida / "fpi-sena-plugin-chatgpt.zip"
    with ZipFile(chatgpt, "w", ZIP_DEFLATED) as z:
        for nombre in ORDEN:
            for f in archivos(SKILLS / nombre):
                z.write(f, f.relative_to(RAIZ))
        for extra in ["plugin.json", ".codex-plugin/plugin.json", "assets/gpt-icon.png", "LICENSE", "NOTICE.md"]:
            z.write(RAIZ / extra, extra)

    # El plugin para ChatGPT («Complementos» / Plugins) también va en dist/, descargable desde GitHub.
    dist_plugin = RAIZ / "dist" / "fpi-sena-plugin-chatgpt.zip"
    dist_plugin.write_bytes(chatgpt.read_bytes())
    generados += [chatgpt, dist_plugin]

    for p in generados:
        with ZipFile(p) as z:
            assert z.testzip() is None
            print(f"{p}  v{version}  {len(z.namelist())} archivos  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
