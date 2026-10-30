# Evaluación en la guía

## Principios (evaluación por competencias)
- Basada en criterios pertinentes al desempeño en contexto.
- Articula lo cualitativo y lo cuantitativo; se centra en lo esencial.
- Retroalimentación continua: no esperar a la evidencia final.

## Momentos
| Momento | Dónde en la guía | Para qué | Juicio |
|---|---|---|---|
| Diagnóstica | 3.1–3.2 (inicio) | Identificar saberes previos | No |
| Formativa | 3.3 (desarrollo) | Seguimiento, retroalimentación y fortalecimiento del desempeño | Sí |
| Sumativa | 3.3 final y 3.4 (cierre) | Valorar el nivel de logro frente a los RA | Sí |

La evaluación busca verificar el logro de los RA, valorar las competencias en sus dimensiones cognitiva, procedimental y actitudinal, identificar fortalezas y aspectos por mejorar y emitir juicios con base en evidencias objetivas. El instructor define las evidencias, elige técnicas e instrumentos acordes con su tipo, garantiza la coherencia actividad–evidencia–evaluación, retroalimenta a tiempo y registra resultados según los lineamientos. El aprendiz debe conocer los criterios e indicadores con que será evaluado.

## Tipos de evidencia → técnica → instrumento
| Evidencia | Qué demuestra | Ejemplos |
|---|---|---|
| **Conocimiento** | Apropiación conceptual: conceptos, teorías, principios que el aprendiz aplica | cuestionarios, pruebas escritas, organizadores gráficos (mapas conceptuales y mentales, cuadros sinópticos, diagramas de flujo, líneas de tiempo, infografías), mentefactos, ensayos |
| **Desempeño** | Cómo ejecuta procesos o procedimientos en contextos reales o simulados (información directa y confiable) | simulaciones, prácticas de laboratorio, ejercicios aplicados, demostraciones, juego de roles |
| **Producto** | Resultados tangibles que cumplen el criterio, según instructivos | informes, proyectos, prototipos, presentaciones digitales, documentos elaborados |

**Parejas técnica → instrumento** (instructivo GFPI-F-135):
| Técnica | Instrumento |
|---|---|
| Ensayo | Rúbrica |
| Organizador gráfico (mapas conceptuales y mentales, cuadros sinópticos, infografías) | Rúbrica |
| Formulación de preguntas | Cuestionario |
| Observación directa | Lista de chequeo |
| Exposición | Lista de chequeo o rúbrica |
| Valoración de producto | Lista de verificación o rúbrica |
| Simulación / entrevista | Guía de observación, escala de valoración |

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
