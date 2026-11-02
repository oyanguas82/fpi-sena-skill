# Formato GFPI-F-134 V05 – Planeación Pedagógica

Fuente: instrucciones de diligenciamiento del propio formato (hoja «Instrucciones»).

## Generalidades
- Objetivo: consolidar la planeación pedagógica del proyecto formativo.
- Lo diligencia el **Equipo de Gestión Curricular** del programa, cada vez que se hace alistamiento del programa.
- Diligenciado, se envía **junto con las guías de aprendizaje** a revisión técnica y metodológica del Equipo Pedagógico de Centro. Se guarda en el SVP y en el repositorio del centro. No se imprime.
- Clasificación de la información (GOR-G-015): Pública, Pública Clasificada o Pública Reservada (marcar con X).

## Encabezado (hoja FASE)
| Casilla | Qué va | JSON |
|---|---|---|
| Fecha de elaboración | Fecha en que se elabora | `fecha` |
| Denominación del programa | Como aparece en el diseño curricular en ejecución | `programa` |
| Modalidad de formación | Presencial, virtual, a distancia, combinada | `modalidad` |
| Código y versión del programa | Como en el diseño curricular | `codigo_version` (`228118 V1`) |
| Nombre y código del proyecto | Como en SOFIA Plus, estado publicado (no aplica en complementaria) | `proyecto`, `codigo_proyecto` |
| Equipo de gestión curricular | Nombres completos de quienes elaboraron la planeación | `equipo` (lista) |
| Regional y centro | Del equipo de gestión curricular | `regional_centro` |

## Columnas (una fila por RA)
| Col. | Casilla | Regla |
|---|---|---|
| A | Fase del proyecto | Fase a la que pertenece la AP (solo titulada) |
| B | Actividad de proyecto | `AP<n>-<nombre>` del proyecto formativo |
| C | Competencia | Código + denominación (catálogo) |
| D | Resultados de aprendizaje | RA asociados a la competencia en esa AP y fase (catálogo) |
| E | Saberes de conceptos y principios | Literales del currículo |
| F | Saberes de proceso | Literales del currículo |
| G | Criterios de evaluación | Literales del programa |
| H | Actividades de aprendizaje | Formuladas en correspondencia con la AP |
| I–J | Duración: horas directas / independientes | Según la suma de los RA que componen la actividad |
| K | Descripción de la evidencia | Indicar si es de **producto, desempeño o conocimiento** |
| L | Estrategias didácticas activas | Las que se usarán en la actividad |
| M | Ambiente | Aula, laboratorio, unidad productiva; virtual = LMS del SENA |
| N | Materiales de formación | Del proyecto formativo; recurso consumible o utilizable, acorde a la modalidad |
| O | Instructores responsables | Número/perfil de instructores |
| P | Observaciones | Opcional |

## Actividad de aprendizaje (columna H)
- Estructura: **verbo en infinitivo + objeto + condición + componente actitudinal**. Ej.: «Planear las actividades de construcción del software a partir del informe de diseño, configurando las herramientas de desarrollo, demostrando responsabilidad y trabajo colaborativo».
- Codificación usada por las guías: `GA1-<competencia>-AA1: <actividad>`. Este texto se copia **textual** en el apartado 3.3 de la guía GFPI-F-135.
- Una AP suele tener varias actividades de aprendizaje: una o más por competencia (técnica y claves/transversales).
- Las evidencias de la columna K usan el código de la guía: `GA1-<competencia>-AA1-EV01`.

## Horas
- Directas + independientes = duración de la actividad. No deben superar las horas del RA (si el catálogo las trae) ni de la competencia.
- El trabajo independiente suele ser una fracción menor de las directas; confírmalo con el instructor (depende del centro y la modalidad).

## JSON
```json
{
  "identificacion": {"fecha": "", "programa": "", "modalidad": "", "codigo_version": "228118 V1",
                     "proyecto": "", "codigo_proyecto": "", "equipo": [""], "regional_centro": "",
                     "clasificacion": "publica"},
  "filas": [
    {"fase": "Planeación", "actividad_proyecto": "AP3-…", "competencia": "220501096", "resultados": ["01"],
     "actividad_aprendizaje": "GA1-220501096-AA1: …", "horas_directas": 40, "horas_independientes": 8,
     "evidencia": "Desempeño: GA1-220501096-AA1-EV01 …\nProducto: GA1-220501096-AA1-EV02 …",
     "estrategias": "", "ambiente": "", "materiales": "", "instructores": "", "observaciones": "",
     "saberes_conceptos": [], "saberes_proceso": [], "criterios": []}
  ]
}
```
- Cada elemento de `filas` es **una actividad de aprendizaje** de una competencia; `resultados` son números de RA. El generador abre una fila del Excel por RA y combina las celdas comunes.
- Competencia, RA, saberes y criterios se completan solos desde el catálogo. Si el RA no trae listas propias, se usan las de la competencia completas; para acotar, pon en `saberes_conceptos`, `saberes_proceso` o `criterios` la selección (copiada literal; el validador lo comprueba).
- `clasificacion`: `publica` (defecto), `clasificada` o `reservada`.
