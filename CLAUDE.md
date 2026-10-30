# Contexto para Claude Code

Proyecto: skill `guia-aprendizaje-sena` (Guías de Aprendizaje SENA, formato GFPI-F-135 V04), compatible con Claude y ChatGPT.

## Reglas del proyecto
- Idioma: español. Respuestas breves y exactas.
- Scripts en Python; `generar_guia.py`, `validar_guia.py` y `buscar_programa.py` usan solo biblioteca estándar. `extraer_estructura.py` requiere `pdfplumber`.
- Nunca inventar contenido curricular: competencias, RA, conocimientos y criterios salen de `data/programas/*.json`.
- No modificar la plantilla `assets/GFPI-F-135 Formato Guia de Aprendizaje.docx`.
- SKILL.md debe mantenerse corto; el detalle va en `references/`.
- Los PDF de estructuras curriculares no se versionan (.gitignore); viven en `../estructuras-curriculares`.

## Probar cambios
1. `python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos <json> --programa <programa.json>`
2. `python skills/guia-aprendizaje-sena/scripts/generar_guia.py --datos <json> --salida salidas/prueba.docx`
