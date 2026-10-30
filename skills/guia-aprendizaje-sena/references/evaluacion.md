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

## Codificación oficial (GA, AA, EV, IE)
| Sigla | Significa | Formato | Ejemplo |
|---|---|---|---|
| GA | Guía de Aprendizaje | `GA<n>` (número de la guía en el proyecto o la ficha) | `GA1` |
| AP | Actividad de Proyecto | `AP<n>-<nombre>` | `AP2-Establecer las especificaciones funcionales del software` |
| AA | Actividad de Aprendizaje | `GA<n>-<competencia>-AA<n>` | `GA1-220501092-AA1` |
| EV | Evidencia de Aprendizaje | `GA<n>-<competencia>-AA<n>-EV<nn>` (dos dígitos; **reinicia en cada AA**) | `GA1-220501092-AA1-EV01`, `GA1-220501092-AA1-EV02`, `GA1-220501092-AA2-EV01` |
| IE | Instrumento de Evaluación | `IE-` + código de la evidencia + tipo | `IE-GA1-220501092-AA1-EV01 Lista de chequeo` |

- Cada competencia de la guía (técnica o clave) numera sus propias AA: `GA1-220501092-AA1` y `GA1-240201528-AA1` pueden coexistir.
- Título de la actividad en 3.3/3.4: `GA1-220501092-AA1: <nombre literal de la planeación>`.
- Texto de la evidencia (actividad y tabla 4): `Evidencia de producto: GA1-220501092-AA1-EV03 mapa de procesos del software a construir` (tipo, código, nombre en minúscula).
- Tipos de IE: `Lista de chequeo`, `Lista de verificación`, `Rúbrica`, `Cuestionario`.
- Archivos: guía `GA1-<competencia técnica>_<nombre corto>.docx`; instrumentos `GA1-<competencia técnica>_Instrumentos.docx`.

## Indicadores (metodología NSCL)
- Desempeño: tercera persona, presente, afirmativo, **verbo + objeto + condición**. Ej.: "Configura el servidor web según la documentación técnica del proveedor."
- Producto: **objeto + verbo + condición**. Ej.: "El diagrama de clases representa las entidades del caso con la notación UML 2.5."
- 4–8 indicadores por instrumento, derivados del criterio oficial; uno por aspecto observable.

## Fila tipo del apartado 4
| Fase | Actividad del proyecto | Actividad de aprendizaje | Evidencia | Criterio | Técnica e instrumento |
|---|---|---|---|---|---|
| Análisis | AP2-Establecer las especificaciones… | GA1-220501092-AA1: Elaborar diagramas de procesos… | Evidencia de conocimiento: GA1-220501092-AA1-EV01 infografía sobre la teoría general de sistemas | (texto literal del criterio) | Técnica: formulación de preguntas. Instrumento: IE-GA1-220501092-AA1-EV01 Lista de chequeo |

Una evidencia puede cubrir varios criterios: escríbelos separados por punto y coma o en filas adicionales.

## Instrumentos opcionales
Si el instructor lo pide, entrega los instrumentos (lista de chequeo, lista de verificación, rúbrica, cuestionario) como anexo Word aparte con `scripts/generar_instrumentos.py`. Detalle y JSON en [instrumentos.md](instrumentos.md).
