# Juicios evaluativos y planes de mejoramiento

## Conceptos
- El juicio evaluativo se emite **por resultado de aprendizaje (RA)**, con base en las evidencias de aprendizaje y sus instrumentos (criterios de evaluación del programa). Se registra en el sistema de gestión académica (SOFIA Plus).
- Valores: **APROBADO**, **NO APROBADO**, **POR EVALUAR** (aún sin evidencias suficientes).
- Evidencia: **A** (aprobada), **D** (no aprobada) o vacía (pendiente). Viene del juicio de cada instrumento (lista de chequeo, rúbrica, cuestionario).
- Regla del script: RA APROBADO solo si **todas** sus evidencias están en A; NO APROBADO si alguna está en D; si no, POR EVALUAR. Si el instructor usa otra regla (p. ej. evidencias opcionales), ajusta la lista de evidencias del RA.
- Plan de mejoramiento: se concierta con el aprendiz para cada RA no aprobado; define actividades, evidencia a entregar y fecha límite. Plazos, número de oportunidades y consecuencias los fija el **Reglamento del Aprendiz SENA vigente** y el centro de formación: pregúntalos al instructor; no los inventes.

## Actividades de mejoramiento (cómo redactarlas)
- Parten de la retroalimentación del instrumento: qué indicador no se cumplió.
- Verbo en infinitivo + qué hace + con qué recurso + cómo demuestra el logro. Ej.: «Corregir el modelo de datos según las observaciones de la lista de chequeo y sustentarlo al instructor».
- 2–4 actividades por RA; la evidencia de mejoramiento debe ser evaluable con los **mismos criterios** del RA (literales del catálogo).
- Fecha límite concreta y realista.

## JSON de entrada (juicios.json)
```json
{
  "identificacion": {"programa": "", "codigo_version": "228118 V1", "ficha": "", "competencia": "",
                     "instructor": "", "fecha_corte": ""},
  "resultados": [{"codigo": "220501096-01", "evidencias": ["GA1-220501096-AA1-EV01", "GA1-220501096-AA1-EV02"]}],
  "aprendices": [{"documento": "", "nombre": "", "evidencias": {"GA1-220501096-AA1-EV01": "A"}, "observaciones": ""}]
}
```
- Las evidencias y RA salen de la tabla 4 de la guía (o de la planeación GFPI-F-134).
- Valores aceptados: A / Aprobado / Cumple / Sí; D / No aprobado / Deficiente / No; vacío = pendiente.
- Si el instructor adjunta una hoja de cálculo o lista de SOFIA/LMS, conviértela a este JSON sin alterar nombres ni documentos.

## JSON de planes (planes.json)
`consolidar_juicios.py --planes` lo crea con los RA no aprobados, sus criterios y las evidencias en D. Completa por RA: `actividades` (lista), `evidencia_mejoramiento`, `fecha_entrega`; por aprendiz: `compromisos`; en identificación: `fecha`.

## Privacidad
Nombres y documentos de aprendices son datos personales: úsalos solo en los archivos del instructor; no los copies a otros documentos, resúmenes ni memoria.
