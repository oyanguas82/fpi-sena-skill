# Historial y estado del proyecto (traspaso desde Claude.ai, 2026-10-29)

## Origen
- Base: plugin ChatGPT "FPI SENA" v0.13.2 (antes GPT) con skill `instructions`, plantilla GFPI-F-135 V04, 6 PDFs de referencia (7 MB) y `generar_guia.py`.
- Objetivo: una skill (estándar SKILL.md) que funcione en Claude y ChatGPT y cree guías desde la estructura curricular oficial.

## Lo hecho (v1.0)
1. Skill renombrada `guia-aprendizaje-sena`; SKILL.md con flujo de 6 pasos: programa → competencia/RA → datos del instructor → diseño → Word → entrega.
2. PDFs de referencia condensados en `references/`: formato-gfpi-f-135, evaluacion, estrategias-didacticas (Pimienta + Manual), bloom, apa7, entrega-word, estructura-curricular.
3. Regla cambiada: el Word se entrega solo al crear/modificar la guía (antes en todas las respuestas).
4. Scripts nuevos:
   - `buscar_programa.py`: consulta el catálogo.
   - `validar_guia.py`: criterios literales vs currículo, RA oficiales, suma de horas, EA de actividades presentes en tabla 4, presentación de 4 párrafos.
   - `extraer_estructura.py`: PDF SOFIA Plus → JSON (pdfplumber).
   - `generar_guia.py`: se añadió campo opcional `titulo` por actividad.
5. Catálogo: 68 programas (867 competencias) en `data/programas/`, índice en `data/indice.json`.

## Hallazgos de los PDF curriculares
- Formato A (15 PDFs): "1. CONTENIDOS CURRICULARES", conocimientos de conceptos y principios, listas sin viñetas.
- Formato B (53 PDFs): "4.CONTENIDOS CURRICULARES", 4.6.1 proceso / 4.6.2 saber / 4.7 criterios; ítems con "*"; en programas recientes agrupados por RA (encabezado = texto del RA + ":") → se asignan a cada RA.
- SOFIA Plus corta texto en saltos de página: 232 advertencias de posible truncado (lista en `../entregables/revision-extraccion.md`).
- Código 999999999 = etapa productiva.
- Las horas por RA casi nunca vienen en el PDF.

## Reglas pedagógicas clave (Formato Explicativo)
- 3.1 y 3.2 no se evalúan; 3.3 copia textual la planeación pedagógica (verbo infinitivo + objeto + condición) y se evalúa; 3.4 transfiere y se evalúa.
- Descripción de actividad: individual/colaborativa, qué hacen, con qué herramienta, cómo socializan.
- Codificación oficial (de guías SENA reales, confirmada por el instructor 2026-10-30): actividad `GA1-220501092-AA1`; evidencia `GA1-220501092-AA1-EV01` (dos dígitos, reinicia por AA); instrumento `IE-GA1-220501092-AA1-EV01 Lista de chequeo`; actividad de proyecto `AP2-…`; archivos `GA1-<competencia técnica>_<nombre>.docx` y `_Instrumentos.docx`.
- Guías con varias competencias: técnica + claves (transversales), RA `220501092-02. … (248 H)`, duración total con desglose Técnico/Claves.
- Duración: "X horas directas y Y de trabajo independiente".

## Sesiones en Claude Code
- 2026-10-29: continuación del desarrollo en Claude Code (VS Code). `CLAUDE.md` importa este historial con `@docs/HISTORIAL.md`, así que se carga en cada sesión. Historial versionado en el commit `3058e44`.
- 2026-10-29 (v1.1): instrumentos de evaluación como anexo Word.
  - `generar_instrumentos.py`: lista de chequeo, lista de verificación, rúbrica (2–5 niveles) y cuestionario con clave de respuestas en página aparte. Reutiliza logo, estilos y márgenes de la plantilla (sin modificarla); pie propio «Anexo: instrumentos de evaluación…».
  - `validar_guia.py --instrumentos`: criterios oficiales, EAn presente en tabla 4, nombre del instrumento igual al de la tabla, 4–8 indicadores, descriptores por nivel, clave del cuestionario e instrumentos de la tabla sin generar. `--datos` ahora es opcional.
  - `references/instrumentos.md` con reglas y JSON; `pruebas/` con guía e instrumentos de ejemplo (ADSO 220501096). Revisado visualmente en Word (PDF).
- 2026-10-29: pruebas (pendiente 1). `empaquetar.py` genera los paquetes v1.1 en `../entregables`. Plan de pruebas y resultados en `docs/PRUEBAS.md`. Hallazgo: 45 competencias con RA fusionados o marcadores «RA n» en las listas (fallo del extractor).
- 2026-10-29: extractor corregido. `extraer_estructura.py` reconoce marcadores de RA en las listas («RA 1», «RA1.», «R.A. 2», «RAP 1», «RA 3 Y 4», «240201524_01») y RA numerados sin espacio («2.EFECTUAR») o con prefijo «RA1»/«RAP 1»; si los RA no tienen número, asigna por posición con aviso; toma las horas del RA cuando el PDF las trae («96H»). Catálogo regenerado: 611 marcadores eliminados de las listas, RA con listas propias 25 → 339, 39 RA con horas. `validar_guia.py` rechaza marcadores como criterio.
- 2026-10-30: distribución multiplataforma. `.claude-plugin/` (plugin + marketplace Claude Code, validado con `claude plugin validate`), `.agents/plugins/marketplace.json` (Codex, sin validar: Codex no instalado), `dist/guia-aprendizaje-sena-skill.zip` (claude.ai y ChatGPT; lo actualiza `empaquetar.py`). Licencia MIT para la obra propia; `NOTICE.md` excluye plantilla, logo y catálogo SENA (públicos para instructores) y resúmenes de obras de terceros. `.claude/skills/` ya no se versiona (junction local).

- 2026-10-30: formato del Word de la guía. `generar_guia.py` pone etiquetas en negrita, justifica el texto, separa actividades y apartados, quita la negrita heredada del párrafo objetivo, aplica sangría francesa a la bibliografía y fija anchos de la tabla 4 (diseño fijo, encabezado repetido, títulos de tabla unidos a su tabla). Revisado en Word (PDF). Convenciones en `references/entrega-word.md`.
- 2026-10-30: codificación GA/AA/EV/IE. Referencias (`evaluacion.md`, `formato-gfpi-f-135.md`, `entrega-word.md`, `instrumentos.md`, SKILL.md) actualizadas; `validar_guia.py` valida formato AA/EV/IE, numeración EV por actividad, GA vs competencia y avisa si queda `EA<n>`; `generar_instrumentos.py` muestra la guía (`identificacion.guia`); `generar_guia.py` pone en negrita el código de evidencia y separa instrumentos por línea. Pruebas ADSO actualizadas (incluye AA1 con EV1 y EV2).
- 2026-10-30: aprendizaje de dos guías reales (228128 V04 presencial y 228118 V01 virtual). Codificación oficial (reemplaza GA/AA/EV con espacios del mismo día), guías multicompetencia (validador por unión de competencias; instrumentos muestran solo su competencia), lineamientos de entrega (`entrega`), código AP, glosario con importancia, `references/ejemplos-guias.md`. Pruebas ADSO con 220501096 + 240201528.

- 2026-10-30: despliegue v1.2.0 (manifiestos de Claude Code, Codex y ChatGPT; paquetes y `dist/` regenerados; etiqueta `v1.2.0`).
- 2026-10-30 (v1.3.0): proyectos formativos. `extraer_proyecto.py` (GFPI-F-016 y verificación de viabilidad) → `data/proyectos/` + `data/indice_proyectos.json`: 37 proyectos, 31 con planeación, 1941 RA (en los 31 coincide con el total declarado en 1.9.1–1.9.3), 1651 enlazados al catálogo curricular. Variantes resueltas: RA sin número, número pegado al código («27050108903.»), rótulos «RA 2:»/«RAP 01.», AP sin numerar (asignadas por fase y orden), fases con errores de digitación, celdas que arrastran texto de la fila anterior, páginas con una sola fila. `buscar_proyecto.py`, `validar_guia.py --proyecto` (AP existe, fase, RA planeados en la AP) y paso 2 del SKILL.md. No se guardan nombres de personas.
- 2026-10-30 (v1.4.0): Instructivo del formato GFPI-F-135 V04 (2026). `formato-gfpi-f-135.md` reescrito: definiciones de identificación, presentación (saludo, propósito formativo, contenidos, «✓ Actividad de Aprendizaje N», mensaje motivador), campos de cada actividad, momentos inicio/desarrollo/cierre, AA = verbo + objeto + condición + componente actitudinal (de la planeación GFPI-F-134), subactividades con qué/modalidad/herramienta/socialización y dominio, transferencia no planeada pero evaluada, bibliografía y webgrafía. Bloom y evaluación (tipos de evaluación, parejas técnica-instrumento) actualizados. Generador: textos introductorios de cada momento, subtítulos Bibliografía/Webgrafía, filas de la tabla 4 sin partir. Validador: avisos de saludo, lista de AA en presentación, componente actitudinal y dominio de subactividades.
- 2026-10-30 (v1.4.1): en ChatGPT la guía salió sin la plantilla (el modelo armó el Word por su cuenta). SKILL.md paso 6: generar SIEMPRE con `generar_guia.py`, ubicar la carpeta de la skill con `find`, nunca python-docx/otra skill; si no hay Python, decirlo y no entregar otro Word. `validar_guia.py --docx` compara byte a byte logo, encabezados, pie y estilos con la plantilla y verifica los 8 apartados. Plugin ChatGPT publicado en `dist/fpi-sena-plugin-chatgpt.zip`; versión del marketplace solo en `plugin.json`.

## Pendiente / ideas
- Proyectos: 6 solo con verificación de viabilidad (sin planeación); Promotor de Salud sin códigos (borrador); 14 con AP numeradas por el extractor; 290 RA sin enlazar (213 de competencias de otra versión del programa: 112005 v101, 723105/723106 v102, 525203, 621201, 723107, 632305).
- Confirmar instalación real: marketplace en Claude Code, `codex plugin marketplace add oyanguas82/fpi-sena-skill`, subida del zip en claude.ai y ChatGPT.
- Programa 838200: criterios partidos palabra por palabra (falla de unión de líneas); otros ítems sueltos tipo «EMPRENDEDORES.», «(3)», «-UTILIZA …».
- Revisar nombres de competencia anómalos en 635503 (240202501, 240201526, 240201530).
- Probar en claude.ai y ChatGPT los casos de `docs/PRUEBAS.md` y anotar resultados.
- Revisar los ítems truncados de los programas más usados.
- Mejorar heurística de unión de líneas en formato A (listas sin viñetas).
- Guía de prueba: `../entregables/Guia_prueba_ADSO_220501096.docx`.
