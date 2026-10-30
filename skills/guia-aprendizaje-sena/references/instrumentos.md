# Instrumentos de evaluación (anexo Word)

Léelo cuando el instructor pida los instrumentos (lista de chequeo, lista de verificación, rúbrica o cuestionario) de una guía.

## Reglas
- Un instrumento por evidencia de la tabla 4. El `codigo` es el nombre IE que figura en la columna «Técnica e instrumento»: `GA1 220501121 - IE Lista de chequeo - AA1 - Mapa mental - EV1` (ver codificación en [evaluacion.md](evaluacion.md)). `identificacion.guia` lleva el código de la guía (`GA1 220501121`).
- `criterios`: copia literal de los criterios oficiales de esa evidencia (los mismos de la tabla 4).
- Indicadores derivados del criterio, uno por aspecto observable, con la sintaxis de [evaluacion.md](evaluacion.md) (desempeño: verbo + objeto + condición; producto: objeto + verbo + condición). Listas: 4–8 indicadores. Rúbrica: 3–8 indicadores.
- Tipo según la evidencia: desempeño → `lista_chequeo` o `rubrica`; producto → `lista_verificacion` o `rubrica`; conocimiento → `cuestionario` o `rubrica`.
- `aprobacion`: condición del juicio «Aprobado» que define el instructor (p. ej. «Cumple la totalidad de los indicadores»). Si no la da, queda pendiente.
- Las casillas Aprendiz, Documento, Fecha, Observaciones, Juicio y Firmas se dejan en blanco para diligenciar a mano.

## Comandos
```
python scripts/generar_instrumentos.py --datos instrumentos.json --salida <ruta>/GA1-<competencia>_Instrumentos.docx
python scripts/validar_guia.py --datos datos.json --instrumentos instrumentos.json --programa <json_del_programa>
```
El validador comprueba criterios oficiales, el formato del código IE, que la GA corresponda a la competencia, que cada `AA - EV` exista en la tabla 4, coherencia de nombres, número de indicadores, descriptores de rúbrica y clave del cuestionario. Corrige los errores antes de entregar.

## JSON
```json
{
  "identificacion": {"guia": "GA1 220501121", "programa": "", "codigo": "", "ficha": "", "competencia": "", "resultados": "", "instructor": ""},
  "instrumentos": [
    {"codigo": "GA1 220501121 - IE Lista de chequeo - AA2 - Configuración del equipo - EV1", "tipo": "lista_chequeo",
     "evidencia": "AA2 - Configuración del equipo - EV1: Evidencia de desempeño – Individual", "actividad": "AA2 - …",
     "criterios": ["criterio literal"], "aprobacion": "",
     "indicadores": ["Indicador 1", "Indicador 2"]},
    {"codigo": "GA1 220501121 - IE Rúbrica - AA3 - Informe técnico - EV1", "tipo": "rubrica", "evidencia": "", "actividad": "",
     "criterios": [""], "aprobacion": "",
     "niveles": ["Excelente", "Bueno", "Aceptable", "Insuficiente"],
     "rubrica": [{"indicador": "", "descriptores": ["", "", "", ""]}]},
    {"codigo": "GA1 220501121 - IE Cuestionario - AA1 - Cuestionario - EV1", "tipo": "cuestionario", "evidencia": "", "actividad": "",
     "criterios": [""], "aprobacion": "",
     "preguntas": [{"enunciado": "", "opciones": ["", "", ""], "respuesta": "b"},
                   {"enunciado": "Pregunta abierta", "respuesta": "respuesta esperada (opcional)"}]}
  ]
}
```
- `identificacion` repite los datos de la guía; `ficha` es opcional.
- Campos opcionales por instrumento: `tecnica` (por defecto según el tipo) e `instrucciones` (texto por defecto según el tipo).
- `niveles`: 2–5 (por defecto los cuatro del ejemplo); cada indicador lleva un descriptor por nivel, del mejor al peor.
- `respuesta`: letra (`"b"`) o índice desde 0. El cuestionario incluye una página final con la clave, solo para el instructor.
- El Word usa el logo y los estilos de la plantilla; el pie dice «Anexo: instrumentos de evaluación – Guía de Aprendizaje GFPI-F-135 V04».
