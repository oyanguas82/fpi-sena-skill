# Contexto para Claude Code

Proyecto: skill `guia-aprendizaje-sena` (Guías de Aprendizaje SENA, formato GFPI-F-135 V04), compatible con Claude y ChatGPT.

## Reglas del proyecto
- Idioma: español. Respuestas breves y exactas.
- Scripts en Python; `generar_guia.py`, `generar_instrumentos.py`, `validar_guia.py`, `buscar_programa.py` y `buscar_proyecto.py` usan solo biblioteca estándar. `extraer_estructura.py` y `extraer_proyecto.py` requieren `pdfplumber`.
- Nunca inventar contenido curricular: competencias, RA, conocimientos y criterios salen de `data/programas/*.json`.
- No modificar la plantilla `assets/GFPI-F-135 Formato Guia de Aprendizaje.docx`.
- SKILL.md debe mantenerse corto; el detalle va en `references/`.
- Los PDF no se versionan (.gitignore): diseños curriculares en `../estructuras-curriculares`, proyectos formativos en `../proyectos-formativos`. Extraer a `data/programas/` y `data/proyectos/` con los scripts `extraer_*`.
- Nunca guardar nombres de personas de los PDF de proyectos.

## Probar cambios
1. `python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos <json> --programa <programa.json>`
2. `python skills/guia-aprendizaje-sena/scripts/generar_guia.py --datos <json> --salida salidas/prueba.docx`
3. Instrumentos: `validar_guia.py --datos <guia> --instrumentos <json> --programa <programa.json>` y `generar_instrumentos.py --datos <json> --salida salidas/instrumentos.docx`
- Datos de prueba en `pruebas/` (ADSO 228118, competencia 220501096).

## Historial
Historial y pendientes: ver @docs/HISTORIAL.md
