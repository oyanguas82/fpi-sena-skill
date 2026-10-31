# Pruebas de la skill en Claude y ChatGPT

Paquetes: `python empaquetar.py` → `../entregables/guia-aprendizaje-sena.skill` (Claude) y `../entregables/fpi-sena-plugin-chatgpt.zip` (ChatGPT).

## Instalación
- **Claude (claude.ai):** Configuración → Capacidades → Skills → subir `guia-aprendizaje-sena.skill`. Requiere la ejecución de código activada.
- **ChatGPT (skill, recomendado):** Plugins (barra lateral) → pestaña Skills → Create → Upload from your computer → `guia-aprendizaje-sena-skill.zip`. Disponible en planes Business, Enterprise, Edu y Healthcare (en Plus/Pro no está confirmado); el administrador puede restringir la subida. Al subirla puede quedar «Needs Review» o «Blocked» tras el escaneo.
- **ChatGPT (plugin):** `fpi-sena-plugin-chatgpt.zip` (manifiesto `plugin.json` en la raíz + `skills/`). En la web lo sube un administrador: Admin console → Plugins → Add → Upload plugin. Para prueba local: app de escritorio, copiando la carpeta a `~/.codex/plugins/` y registrándola en `~/.agents/plugins/marketplace.json`.

## Casos
Use un chat nuevo por caso. Escriba como instructor, sin mencionar el nombre de la skill.

| # | Mensaje inicial | Qué debe pasar |
|---|---|---|
| 1 | «Necesito una guía de aprendizaje para ADSO, competencia de construcción del software, RA de planear actividades.» | Activa la skill, encuentra 228118, muestra RA 01 con criterios literales y pide los datos del paso 3. |
| 2 | Continuar el caso 1 con datos completos (proyecto, fase, actividades de la planeación, 48 h). | Entrega `.docx` descargable; resumen, matriz conocimiento → actividad y pendientes. Criterios de la tabla 4 literales. |
| 3 | «Ahora genérame los instrumentos de evaluación de esa guía.» | Entrega un segundo `.docx` (`GA1-<competencia>_Instrumentos.docx`) con un instrumento por evidencia `GA1-<competencia>-AAn-EVnn`, nombrado `IE-GA1-<competencia>-AAn-EVnn <tipo>`; criterios literales; clave del cuestionario aparte. |
| 4 | «Hazme una guía para Cocina 635503, competencia manipular alimentos.» | Muestra los 3 RA por separado, cada uno con sus conocimientos y criterios (corregido en el catálogo). |
| 5 | «Guía rápida para la competencia de inglés de cualquier programa, sin más datos.» | Genera borrador con `[Pendiente de información del instructor]`; no inventa criterios. |
| 6 | «¿Qué diferencia hay entre evidencia de desempeño y de producto?» | Responde en el chat, sin generar Word. |
| 8 | «Guía para ADSO, proyecto de mi centro, actividad de proyecto de diseño.» | Encuentra el proyecto 2480542, muestra fases y AP, propone AP3 con sus competencias y RA planeados. |
| 7 | Adjuntar un PDF de diseño curricular que no esté en el catálogo y pedir una guía. | Ejecuta `extraer_estructura.py` (si el entorno tiene `pdfplumber`) o pide pegar el contenido. |

## Lista de revisión por caso
- [ ] La skill se activó sola.
- [ ] Competencia, RA y criterios coinciden con el currículo (sin redacción propia presentada como oficial).
- [ ] El Word abre en Microsoft Word, conserva logo, pie «GFPI-F-135 V04» y los 8 apartados.
- [ ] Horas de actividades = duración de la guía.
- [ ] Se ejecutó `validar_guia.py` (con `--docx`) y se corrigieron errores; el Word salió de la plantilla, no de python-docx.
- [ ] No se entregó Word en preguntas conceptuales.

## Resultados
| Fecha | Plataforma | Caso | Resultado | Observaciones |
|---|---|---|---|---|
| 2026-10-29 | Claude Code (local) | 3 | OK | Instrumentos ADSO 220501096 generados y validados; revisión visual en Word. |
| 2026-10-29 | Claude Code (local) | 4 | Falla de datos | 290801023 y 260201057: listas con marcadores «RA n» y RA fusionados. |
| 2026-10-29 | Claude Code (local) | 4 | Corregido | Extractor ajustado y catálogo regenerado; 290801023 sale con 3 RA y listas propias. |

## Hallazgos de datos (2026-10-29)
- 45 de 867 competencias (23 programas) tienen problemas de extracción:
  - 37 con marcadores «RA 1», «RA 2»… como ítems de conocimientos/criterios (no se asignan a cada RA).
  - 10 con varios RA fusionados en uno (p. ej. 635503 → 290801023: «3 … 2. … 1. …»).
  - Más afectados: 837501 (9), 836138 (7), 635503, 664212, 834258 (3 c/u).
- Competencias con nombre anómalo en 635503: 240202501 (inicio perdido), 240201526 (prefijo «Enrique Low Murtra-»), 240201530 («Resultado de Aprendizaje de la Inducción.»).
- El validador acepta «RA 1» como criterio oficial porque figura en la lista.
- **Estado:** marcadores y RA fusionados corregidos el mismo día (ver HISTORIAL). Pendiente: 838200 (criterios partidos palabra por palabra) y nombres anómalos de 635503.
