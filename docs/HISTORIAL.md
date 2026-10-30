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
- Evidencias EA1, EA2…; instrumentos `EA1_Lista_Chequeo_Desempeño_<Nombre>`.
- Duración: "X horas directas y Y de trabajo independiente".

## Sesiones en Claude Code
- 2026-10-29: continuación del desarrollo en Claude Code (VS Code). `CLAUDE.md` importa este historial con `@docs/HISTORIAL.md`, así que se carga en cada sesión. Historial versionado en el commit `3058e44`.
- 2026-10-29 (v1.1): instrumentos de evaluación como anexo Word.
  - `generar_instrumentos.py`: lista de chequeo, lista de verificación, rúbrica (2–5 niveles) y cuestionario con clave de respuestas en página aparte. Reutiliza logo, estilos y márgenes de la plantilla (sin modificarla); pie propio «Anexo: instrumentos de evaluación…».
  - `validar_guia.py --instrumentos`: criterios oficiales, EAn presente en tabla 4, nombre del instrumento igual al de la tabla, 4–8 indicadores, descriptores por nivel, clave del cuestionario e instrumentos de la tabla sin generar. `--datos` ahora es opcional.
  - `references/instrumentos.md` con reglas y JSON; `pruebas/` con guía e instrumentos de ejemplo (ADSO 220501096). Revisado visualmente en Word (PDF).
- 2026-10-29: pruebas (pendiente 1). `empaquetar.py` genera los paquetes v1.1 en `../entregables`. Plan de pruebas y resultados en `docs/PRUEBAS.md`. Hallazgo: 45 competencias con RA fusionados o marcadores «RA n» en las listas (fallo del extractor).
- 2026-10-29: extractor corregido. `extraer_estructura.py` reconoce marcadores de RA en las listas («RA 1», «RA1.», «R.A. 2», «RAP 1», «RA 3 Y 4», «240201524_01») y RA numerados sin espacio («2.EFECTUAR») o con prefijo «RA1»/«RAP 1»; si los RA no tienen número, asigna por posición con aviso; toma las horas del RA cuando el PDF las trae («96H»). Catálogo regenerado: 611 marcadores eliminados de las listas, RA con listas propias 25 → 339, 39 RA con horas. `validar_guia.py` rechaza marcadores como criterio.

## Pendiente / ideas
- Programa 838200: criterios partidos palabra por palabra (falla de unión de líneas); otros ítems sueltos tipo «EMPRENDEDORES.», «(3)», «-UTILIZA …».
- Revisar nombres de competencia anómalos en 635503 (240202501, 240201526, 240201530).
- Probar en claude.ai y ChatGPT los casos de `docs/PRUEBAS.md` y anotar resultados.
- Revisar los ítems truncados de los programas más usados.
- Mejorar heurística de unión de líneas en formato A (listas sin viñetas).
- Guía de prueba: `../entregables/Guia_prueba_ADSO_220501096.docx`.
