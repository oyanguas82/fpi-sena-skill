# Procedimiento de entrega Word

Léelo antes de generar o actualizar el Word de la guía.

1. Recupera la guía vigente y las fuentes curriculares disponibles. Si no existe una guía, parte de `assets/GFPI-F-135 Formato Guia de Aprendizaje.docx`, relativo a la raíz de esta habilidad.
2. Prepara el contenido dentro de los ocho apartados originales. No borres apartados por falta de información: usa campos pendientes. Sustituye los textos de orientación de la plantilla por el contenido desarrollado.
3. Puedes usar el generador incluido: `python scripts/generar_guia.py --datos datos.json --salida /ruta/escribible/Guia_de_Aprendizaje_GFPI-F-135.docx`. Resuelve la ruta del script respecto a esta habilidad, no al directorio de trabajo. El generador encuentra la plantilla empaquetada automáticamente. El JSON debe ser UTF-8.
4. Conserva los valores ya conocidos en cada ejecución: el generador crea una nueva copia desde la plantilla; no fusiona automáticamente el contenido de una entrega anterior.
5. Ejecuta `python scripts/validar_guia.py --datos datos.json --programa <json_del_programa> --docx <guía.docx>` y corrige los errores. `--docx` confirma que el Word salió de la plantilla oficial (si no, regenéralo con `generar_guia.py`; nunca con python-docx u otra librería). Verifica también las ocho secciones, las cuatro fases de actividades, datos faltantes identificados y consistencia de las horas con el currículo. El generador comprueba integridad ZIP/XML y conservación byte a byte de todos los componentes salvo el cuerpo editable del documento, incluidos el logo, los encabezados, los pies, los estilos y las relaciones.
6. Abre o renderiza el Word, si el entorno lo permite, y corrige recortes, tablas ilegibles, espacios anómalos y saltos de página. No afirmes revisión visual si solo se comprobó la estructura.
7. Adjunta el archivo real con el mecanismo de archivos del entorno y un enlace descargable. Añade un resumen breve en el chat. No entregues solo una ruta interna que el usuario no pueda abrir.

## Datos para el generador

Todos los campos son opcionales; los omitidos producen un borrador marcado como pendiente. Para una guía completa, diligencia todos los campos pertinentes. Cada matriz debe contener filas de cadenas y conservar el número de columnas indicado. Los arreglos de actividades permiten más de una actividad por momento. No uses Markdown para simular tablas dentro de celdas.

```json
{
  "identificacion": {
    "programa": "",
    "codigo": "",
    "proyecto": "",
    "fase": "",
    "actividad_proyecto": "",
    "competencia": "",
    "resultados": "",
    "duracion": "56 horas\nTécnico: 48 horas\nClaves: 8 horas"
  },
  "presentacion": ["Párrafo 1", "Párrafo 2", "Párrafo 3", "Párrafo 4"],
  "contexto_actividades": "",
  "actividades": {
    "3.1": [{"descripcion": "", "ambiente": "", "estrategias": "", "materiales": "", "apoyo": "", "duracion": ""}],
    "3.2": [{"descripcion": "", "ambiente": "", "estrategias": "", "materiales": "", "apoyo": "", "duracion": ""}],
    "3.3": [{"titulo": "", "descripcion": "", "ambiente": "", "estrategias": "", "materiales": "", "apoyo": "", "evidencias": "", "entrega": "", "instrumentos": "", "duracion": ""}],
    "3.4": [{"titulo": "", "descripcion": "", "ambiente": "", "estrategias": "", "materiales": "", "apoyo": "", "evidencias": "", "entrega": "", "instrumentos": "", "duracion": ""}]
  },
  "evidencias": [["Fase", "Actividad del proyecto", "Actividad de aprendizaje", "Evidencia", "Criterio oficial", "Técnica e instrumento"]],
  "glosario": ["Término: definición. Importancia: …"],
  "bibliografia": ["Referencia verificada"],
  "control_documento": [["Nombre", "Cargo", "Dependencia", "Fecha"]],
  "cambios": []
}
```

El texto introductorio del apartado 3 y el de cada momento (3.1 inicio, 3.2 inicio, 3.3 desarrollo, 3.4 cierre), sugeridos por el instructivo del formato, se insertan automáticamente; no los repitas en el JSON. El campo `contexto_actividades` lo complementa con el contexto de la competencia. Cada descripción puede incluir varios párrafos separados por saltos de línea.

`evidencias` tiene seis columnas. `control_documento` tiene cuatro (el generador conserva "Autor (es)" en la primera columna de la tabla). `cambios` tiene cinco: nombre, cargo, dependencia, fecha y razón. Para una primera elaboración, usa `"cambios": []`, que deja "No aplica: primera elaboración" en la razón del cambio sin inventar autoría. Si omites `cambios`, quedará pendiente de confirmar si hubo ajustes.

Al elaborar la guía, sustituye los textos ilustrativos del ejemplo por información sustentada y desarrolla las actividades conforme a las instrucciones pedagógicas. El script organiza el documento, pero no verifica por sí solo la validez curricular ni que las referencias sean auténticas.

## Formato automático
El generador da formato al contenido; no uses Markdown (`**`, `#`, viñetas) dentro de los textos:
- Identificación y campos de actividades: etiqueta en negrita y valor en texto normal, justificado.
- `titulo` de actividad en negrita, con espacio antes; párrafos de presentación y contexto justificados.
- Glosario: escribe `Término: definición` (el término sale en negrita).
- Bibliografía: sangría francesa APA; las entradas `"Bibliografía"` y `"Webgrafía"` salen como subtítulos en negrita.
- Presentación: el párrafo 3 lista las actividades en líneas `✓ Actividad de Aprendizaje N: …`.
- Códigos oficiales (`GA1-…-AA1`, `GA1-…-EV01`, `IE-GA1-…`) en negrita dondequiera que aparezcan.
- Identificación con varias líneas: `Técnicas:`, `Claves:` y el código inicial de cada competencia o RA en negrita.
- `entrega`: una línea por rótulo (`Producto: …`, `Formato: …`, `Extensión: …`, `Envío: …`); el rótulo sale en negrita.
- Glosario: `Término: definición. Importancia: …` (término e «Importancia» en negrita, en dos renglones).
- Tabla 4: criterios separados por `;` van en párrafos aparte; en la última columna escribe `Técnica: … Instrumento: …` (cada etiqueta en negrita y en su línea).

## Convenciones de contenido
- `identificacion.competencia`: `código – denominación` literal; con varias competencias, bloques `Técnicas:` / `Claves:` y una competencia por línea.
- `identificacion.resultados`: un RA por línea (`\n`), literal, con código y horas: `220501092-02. Realizar … (248 H)`.
- `identificacion.actividad_proyecto`: `AP2-<nombre>`.
- Cada actividad acepta `titulo` opcional (línea antes de sus campos). En 3.3 y 3.4 úsalo para `GA1-<competencia>-AA<n>: <texto literal de la planeación>`; en `descripcion` inicia con la numeración `3.3.x …`.
- Codificación GA/AA/EV/IE y nombres de archivo: ver [evaluacion.md](evaluacion.md).
- `duracion` de cada actividad: `X horas directas y Y horas de trabajo independiente`.
- En 3.1 y 3.2 omite `evidencias` e `instrumentos` (no se evalúan).
- `evidencias[i][4]` (criterio) debe ser idéntico a un criterio del programa; el validador lo comprueba.
