# Proyectos formativos: catálogo y uso en la guía

## Dónde está
- `data/indice_proyectos.json`: proyectos disponibles (código, nombre, programa, versión, nº de AP y RA).
- `data/proyectos/<código>.json`: un archivo por proyecto (formato GFPI-F-016 de SOFIA Plus).
- Algunos proyectos solo tienen la **verificación de viabilidad** (código y nombre, sin planeación): úsalos para el nombre del proyecto y pide al instructor la fase, la AP y los RA.

## Consultar (siempre por script)
```
python scripts/buscar_proyecto.py --programa 228118                  # proyectos del programa
python scripts/buscar_proyecto.py --buscar "software"                # por nombre o código
python scripts/buscar_proyecto.py --proyecto 2480542                 # problema, objetivos, productos, ambiente, fases y AP
python scripts/buscar_proyecto.py --proyecto 2480542 --actividad AP3 # competencias y RA planeados en la AP
```

## Cómo usarlo al diseñar la guía
1. Con el programa identificado, busca su proyecto y muéstrale al instructor las fases y actividades de proyecto (AP). Si hay varios proyectos o ninguno, pregunta.
2. El instructor elige la AP de la guía. `--actividad` lista las competencias y RA planeados en ella: son la base para elegir las competencias técnicas y claves de la guía (paso 2).
3. Llena la identificación con datos del proyecto: nombre del proyecto, fase de la AP y `actividad_proyecto` = `AP3-<nombre de la AP>`.
4. Contextualiza la guía con el proyecto: la situación problémica de 3.1 sale del **planteamiento del problema**; las evidencias de 3.4 aportan a los **productos** del proyecto; el **ambiente** del proyecto orienta «Ambiente requerido».
5. Valida con `validar_guia.py … --proyecto data/proyectos/<código>.json`: comprueba que la AP exista, su fase y que los RA de la guía estén planeados en esa AP.

## Esquema
```json
{"proyecto": {"codigo": "2480542", "nombre": "…", "programa_codigo": "228118", "programa_version": "1",
              "programa": "…", "centro": "…", "regional": "…", "duracion_meses": 27, "catalogo": "228118_v1.json"},
 "planteamiento": "…", "justificacion": "…", "objetivo_general": "…", "objetivos_especificos": ["…"],
 "beneficiarios": "…", "impacto": {"social": "…"}, "productos": ["…"], "ambiente": "…",
 "fases": [{"fase": "ANÁLISIS", "actividades": [{"numero": 2, "codigo": "AP2", "nombre": "…",
   "resultados": [{"competencia": "220501092", "competencia_texto": "…", "ra": "01", "ra_id_sofia": "593117",
                   "ra_texto": "texto del PDF", "ra_texto_oficial": "texto del catálogo", "en_catalogo": true}]}]}],
 "advertencias": ["…"]}
```
- Usa siempre `ra_texto_oficial` (catálogo curricular). Si `en_catalogo` es `false`, el proyecto es de otra versión del programa o el texto no coincide: muéstralo como «por verificar» y no lo presentes como oficial.
- En 14 proyectos las AP no venían numeradas en el PDF; los números AP1, AP2… se asignaron por fase y orden (ver `advertencias`). Confírmalos con el instructor.

## Agregar o actualizar proyectos
```
python scripts/extraer_proyecto.py "<proyecto>.pdf" --salida data/proyectos
python scripts/extraer_proyecto.py "<carpeta con PDFs>" --salida data/proyectos   # lote + índice
```
Requiere `pdfplumber`. Los PDF viven fuera del repositorio (`../proyectos-formativos`). El extractor no guarda nombres de personas y compara el número de RA extraídos con el que declara el proyecto (1.9.1–1.9.3).
