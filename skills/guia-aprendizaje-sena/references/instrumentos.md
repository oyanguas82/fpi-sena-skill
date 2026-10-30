# Instrumentos de evaluación (anexo Word)

Léelo cuando el instructor pida los instrumentos (lista de chequeo, lista de verificación, rúbrica o cuestionario) de una guía.

## Reglas
- Un instrumento por evidencia `EAn` de la tabla 4. El `codigo` es el mismo nombre que figura en la columna «Técnica e instrumento» (p. ej. `EA2_Lista_Chequeo_Desempeño_<Nombre>`).
- `criterios`: copia literal de los criterios oficiales de esa evidencia (los mismos de la tabla 4).
- Indicadores derivados del criterio, uno por aspecto observable, con la sintaxis de [evaluacion.md](evaluacion.md) (desempeño: verbo + objeto + condición; producto: objeto + verbo + condición). Listas: 4–8 indicadores. Rúbrica: 3–8 indicadores.
- Tipo según la evidencia: desempeño → `lista_chequeo` o `rubrica`; producto → `lista_verificacion` o `rubrica`; conocimiento → `cuestionario` o `rubrica`.
- `aprobacion`: condición del juicio «Aprobado» que define el instructor (p. ej. «Cumple la totalidad de los indicadores»). Si no la da, queda pendiente.
- Las casillas Aprendiz, Documento, Fecha, Observaciones, Juicio y Firmas se dejan en blanco para diligenciar a mano.

## Comandos
```
python scripts/generar_instrumentos.py --datos instrumentos.json --salida <ruta>/Instrumentos_<programa>_<competencia>.docx
python scripts/validar_guia.py --datos datos.json --instrumentos instrumentos.json --programa <json_del_programa>
```
El validador comprueba criterios oficiales, que cada `EAn` exista en la tabla 4, coherencia de nombres, número de indicadores, descriptores de rúbrica y clave del cuestionario. Corrige los errores antes de entregar.

## JSON
```json
{
  "identificacion": {"programa": "", "codigo": "", "ficha": "", "competencia": "", "resultados": "", "instructor": ""},
  "instrumentos": [
    {"codigo": "EA2_Lista_Chequeo_Desempeño_<Nombre>", "tipo": "lista_chequeo",
     "evidencia": "EA2: Evidencia de desempeño: …", "actividad": "Actividad de Aprendizaje 2: …",
     "criterios": ["criterio literal"], "aprobacion": "",
     "indicadores": ["Indicador 1", "Indicador 2"]},
    {"codigo": "EA3_Rúbrica_Producto_<Nombre>", "tipo": "rubrica", "evidencia": "", "actividad": "",
     "criterios": [""], "aprobacion": "",
     "niveles": ["Excelente", "Bueno", "Aceptable", "Insuficiente"],
     "rubrica": [{"indicador": "", "descriptores": ["", "", "", ""]}]},
    {"codigo": "EA1_Cuestionario_Conocimiento_<Nombre>", "tipo": "cuestionario", "evidencia": "", "actividad": "",
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
