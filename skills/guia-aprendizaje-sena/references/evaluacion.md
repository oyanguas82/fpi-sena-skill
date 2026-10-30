# Evaluación en la guía

## Principios (evaluación por competencias)
- Basada en criterios pertinentes al desempeño en contexto.
- Articula lo cualitativo y lo cuantitativo; se centra en lo esencial.
- Retroalimentación continua: no esperar a la evidencia final.

## Momentos
| Momento | Dónde en la guía | Juicio |
|---|---|---|
| Diagnóstica | 3.1–3.2 | No |
| Formativa / continua | 3.3 | Sí |
| Sumativa | 3.3 final y 3.4 | Sí |

## Tipos de evidencia → técnica → instrumento
| Evidencia | Qué demuestra | Técnicas | Instrumentos |
|---|---|---|---|
| **Conocimiento** | Conceptos, teorías, principios (saber) | Formulación de preguntas; ensayo; organizador gráfico | Cuestionario; rúbrica |
| **Desempeño** | Cómo ejecuta el proceso técnico (hacer observable) | Observación directa; exposición; simulación | Lista de chequeo; rúbrica |
| **Producto** | Resultado tangible que cumple especificaciones | Valoración de producto | Lista de verificación; rúbrica |

Relación con el currículo:
- Conocimientos de **saber** → evidencias de conocimiento.
- Conocimientos de **proceso** → evidencias de desempeño y producto.
- **Criterios de evaluación** → columna 5 (literal) y base de los indicadores del instrumento.

## Codificación (GA, AA, EV, IE)
| Sigla | Significa | Formato | Ejemplo |
|---|---|---|---|
| GA | Guía de Aprendizaje | `GA<n> <código competencia>` (n = número de la guía en la competencia) | `GA1 220501121` |
| AA | Actividad de Aprendizaje | `AA<n> - <nombre de la actividad>` | `AA1 - Identificar las herramientas ofimáticas…` |
| EV | Evidencia de Aprendizaje | `AA<n> - <nombre de la evidencia> - EV<m>` (EV **reinicia en cada AA**) | `AA1 - Mapa mental - EV1`, `AA1 - Exposición - EV2`, `AA2 - Taller - EV1` |
| IE | Instrumento de Evaluación | `GA<n> <competencia> - IE <tipo> - AA<n> - <evidencia> - EV<m>` | `GA1 220501121 - IE Lista de chequeo - AA1 - Mapa mental - EV1` |

- Las AA se numeran en orden en 3.3 y 3.4 (3.1 y 3.2 no llevan AA porque no se evalúan).
- Texto de la evidencia en 3.3/3.4 y en la tabla 4: `AA1 - Mapa mental - EV1: Evidencia de conocimiento – Individual|Equipo`.
- Tipos de IE: `Lista de chequeo`, `Lista de verificación`, `Rúbrica`, `Cuestionario`.
- Archivos: guía `GA1-220501121_<nombre corto>.docx`; instrumentos `GA1-220501121_Instrumentos.docx`.

## Indicadores (metodología NSCL)
- Desempeño: tercera persona, presente, afirmativo, **verbo + objeto + condición**. Ej.: "Configura el servidor web según la documentación técnica del proveedor."
- Producto: **objeto + verbo + condición**. Ej.: "El diagrama de clases representa las entidades del caso con la notación UML 2.5."
- 4–8 indicadores por instrumento, derivados del criterio oficial; uno por aspecto observable.

## Fila tipo del apartado 4
| Fase | Actividad del proyecto | Actividad de aprendizaje | Evidencia | Criterio | Técnica e instrumento |
|---|---|---|---|---|---|
| Análisis | Identificar requisitos… | AA1 - Identificar… | AA1 - Cuestionario - EV1: Evidencia de conocimiento – Individual | (texto literal del criterio) | Técnica: formulación de preguntas. Instrumento: GA1 220501121 - IE Cuestionario - AA1 - Cuestionario - EV1 |

Una evidencia puede cubrir varios criterios: escríbelos separados por punto y coma o en filas adicionales.

## Instrumentos opcionales
Si el instructor lo pide, entrega los instrumentos (lista de chequeo, lista de verificación, rúbrica, cuestionario) como anexo Word aparte con `scripts/generar_instrumentos.py`. Detalle y JSON en [instrumentos.md](instrumentos.md).
