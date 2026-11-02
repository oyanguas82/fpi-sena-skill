# Contexto para Codex

Proyecto: plugin «FPI SENA» (agente FPI) con cinco skills: `guia-aprendizaje-sena` (núcleo: catálogo, buscadores, plantilla GFPI-F-135), `planeacion-pedagogica-sena` (GFPI-F-134, Excel), `instrumentos-evaluacion-sena`, `juicios-evaluativos-sena` y `asistente-fpi-sena` (orquestador). Compatible con Codex y ChatGPT. Las skills no núcleo ubican el núcleo como carpeta hermana o con `find`.

## Reglas del proyecto
- Idioma: español. Respuestas breves y exactas.
- Scripts en Python; `generar_guia.py`, `generar_instrumentos.py`, `validar_guia.py`, `buscar_programa.py` y `buscar_proyecto.py` usan solo biblioteca estándar. `extraer_estructura.py` y `extraer_proyecto.py` requieren `pdfplumber`.
- Nunca inventar contenido curricular: competencias, RA, conocimientos y criterios salen de `data/programas/*.json`.
- No modificar las plantillas `assets/GFPI-F-135 Formato Guia de Aprendizaje.docx` ni `planeacion-pedagogica-sena/assets/GFPI-F-134 Formato Planeacion Pedagogica.xlsx`. `scripts/plantilla.py` y `scripts/plantilla_f134.py` son copias incrustadas (base64) que regenera `empaquetar.py`; no editarlas a mano.
- Scripts nuevos: solo biblioteca estándar (los Excel se escriben editando el XML de la plantilla o con `juicios-evaluativos-sena/scripts/xlsx_simple.py`).
- Nunca guardar nombres ni documentos de aprendices en el repositorio (pruebas con datos ficticios).
- SKILL.md debe mantenerse corto; el detalle va en `references/`.
- Los PDF no se versionan (.gitignore): diseños curriculares en `../estructuras-curriculares`, proyectos formativos en `../proyectos-formativos`. Extraer a `data/programas/` y `data/proyectos/` con los scripts `extraer_*`.
- Nunca guardar nombres de personas de los PDF de proyectos.

## Probar cambios
1. `python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos <json> --programa <programa.json>`
2. `python skills/guia-aprendizaje-sena/scripts/generar_guia.py --datos <json> --salida salidas/prueba.docx` y `validar_guia.py --docx salidas/prueba.docx` (confirma que salió de la plantilla)
3. Instrumentos: `validar_guia.py --datos <guia> --instrumentos <json> --programa <programa.json>` y `generar_instrumentos.py --datos <json> --salida salidas/instrumentos.docx`
4. Planeación: `generar_planeacion.py --datos pruebas/planeacion_adso_ap3.json --salida salidas/planeacion.xlsx` y `validar_planeacion.py --datos … --proyecto skills/guia-aprendizaje-sena/data/proyectos/2480542.json --xlsx salidas/planeacion.xlsx`
5. Juicios: `consolidar_juicios.py --datos pruebas/juicios_adso_ficha_prueba.json --salida salidas/juicios.xlsx --planes salidas/planes.json` y `generar_plan_mejoramiento.py --datos salidas/planes.json --salida salidas/planes.docx`
6. `python empaquetar.py` y `claude plugin validate .`
- Datos de prueba en `pruebas/` (ADSO 228118, competencia 220501096, proyecto 2480542).

## Historial
Historial y pendientes: ver @docs/HISTORIAL.md
