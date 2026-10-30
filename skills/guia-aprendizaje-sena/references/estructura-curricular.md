# Estructura curricular: catálogo y extracción

## Dónde está
- `data/indice.json`: programas disponibles (código, versión, denominación, nivel, archivo, nº de advertencias).
- `data/programas/<codigo>_v<version>.json`: un archivo por programa (68 programas cargados).

## Consultar (siempre por script; no leas el JSON completo)
```
python scripts/buscar_programa.py --buscar "desarrollo software"          # por nombre o código
python scripts/buscar_programa.py --programa 228118 --competencias         # lista de competencias
python scripts/buscar_programa.py --programa 228118 --competencia 220501096 # detalle completo
```

## Esquema
```json
{
  "programa": {"codigo": "228118", "version": "1", "denominacion": "...", "nivel": "Tecnologo",
               "duracion_lectiva_horas": 3120, "duracion_productiva_horas": 864,
               "formato_reporte": "A|B", "fuente": "archivo.pdf"},
  "competencias": [{
    "codigo": "220501096",
    "denominacion": "Norma / unidad de competencia (texto para la guía)",
    "nombre_corto": "Nombre de la competencia (solo formato B)",
    "duracion_horas": 1008,
    "resultados": [{
      "numero": "01", "denominacion": "...", "duracion_horas": null,
      "conocimientos_saber": ["..."], "conocimientos_proceso": ["..."], "criterios_evaluacion": ["..."]
    }],
    "conocimientos_saber": ["..."], "conocimientos_proceso": ["..."], "criterios_evaluacion": ["..."],
    "etapa_productiva": true
  }],
  "advertencias": ["Competencia X criterios: posible texto truncado: «…»"]
}
```

## Cómo usarlo al diseñar la guía
- **Si el RA trae sus propias listas** (`resultados[i].conocimientos_*` / `criterios_evaluacion`): úsalas; el diseño curricular ya las asoció a ese RA (por encabezado del RA o por marcadores «RA 1», «RAP 2», «240201524_01» en el PDF). Si la advertencia dice «asignados por posición», el PDF no numeraba los RA: muestra la asignación al instructor para que la confirme.
- **Si no**: las listas están solo a nivel de competencia; selecciona las que correspondan a los RA elegidos y muéstrale al instructor la selección.
- `denominacion` de la competencia es el texto que va en la guía (en formato B corresponde a "Norma / unidad de competencia").
- Los textos vienen en MAYÚSCULAS. Puedes pasarlos a mayúscula inicial **sin cambiar palabras**; el validador compara sin distinguir mayúsculas ni tildes.
- `duracion_horas` del RA casi siempre es `null` (solo unos 40 RA traen horas en el PDF): si falta, pide las horas al instructor (planeación pedagógica).
- Competencias con código `999999999` = etapa productiva; no se usan para guías.
- **Advertencias**: el reporte de SOFIA Plus a veces corta texto en los saltos de página. Si un ítem que vas a usar aparece en `advertencias` (o empieza con "…"), avisa al instructor y pídele confirmar el texto completo.

## Agregar o actualizar programas
```
python scripts/extraer_estructura.py "<diseño curricular>.pdf" --salida data/programas
python scripts/extraer_estructura.py "<carpeta con PDFs>" --salida data/programas   # lote + índice
```
Requiere `pdfplumber`. Soporta los dos formatos del reporte SOFIA Plus: A ("1. Contenidos curriculares", conocimientos de conceptos y principios) y B ("4. Contenidos curriculares", conocimientos del saber, a veces agrupados por RA). Si el instructor adjunta un PDF que no está en el catálogo, extráelo a una carpeta escribible y usa ese JSON con `--archivo`.
