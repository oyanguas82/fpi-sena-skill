# FPI SENA – Agente de Formación Profesional Integral

Plugin con cinco skills (estándar SKILL.md) para Claude, Claude Code, Codex y ChatGPT que acompaña el ciclo FPI a partir de la estructura curricular y el proyecto formativo oficiales:

| Skill | Produce |
|---|---|
| `guia-aprendizaje-sena` (núcleo: catálogo, buscadores, plantilla) | Guía GFPI-F-135 V04 en Word |
| `planeacion-pedagogica-sena` | Planeación GFPI-F-134 V05 en Excel |
| `instrumentos-evaluacion-sena` | Listas de chequeo/verificación, rúbricas y cuestionarios (Word) |
| `juicios-evaluativos-sena` | Juicios por RA (Excel) y planes de mejoramiento (Word) |
| `asistente-fpi-sena` | Orienta y encadena el ciclo |

Las skills usan el catálogo de `guia-aprendizaje-sena`: instálela siempre. En Claude Code hay además el agente `asistente-fpi` y los comandos `/fpi`, `/planeacion`, `/guia`, `/instrumentos` y `/juicios`.

**Página de descargas:** https://oyanguas82.github.io/fpi-sena-skill/

## Estructura
```
plugin.json                      Manifiesto del plugin (Codex / ChatGPT, formato portátil)
.codex-plugin/plugin.json        Manifiesto Codex (compatibilidad)
.agents/plugins/marketplace.json Marketplace para Codex / ChatGPT
.claude-plugin/                  Plugin y marketplace para Claude Code
agents/asistente-fpi.md          Agente orquestador (Claude Code)
commands/                        /fpi /planeacion /guia /instrumentos /juicios (Claude Code)
dist/                            Una <skill>-skill.zip por skill (claude.ai y ChatGPT › Skills) y plugin (.zip, ChatGPT › Complementos)
skills/planeacion-pedagogica-sena/   generar_planeacion, validar_planeacion; plantilla GFPI-F-134 (assets/ e incrustada)
skills/instrumentos-evaluacion-sena/ flujo de instrumentos (usa los scripts del núcleo)
skills/juicios-evaluativos-sena/     consolidar_juicios, generar_plan_mejoramiento
skills/asistente-fpi-sena/           orquestador
skills/guia-aprendizaje-sena/
  SKILL.md                       Instrucciones y flujo
  references/                    Reglas del formato, evaluación, estrategias, Bloom, APA
  scripts/                       generar_guia, generar_instrumentos, validar_guia, buscar_programa, buscar_proyecto, extraer_estructura, extraer_proyecto
  data/                          Catálogo curricular (68 programas) y proyectos formativos (37)
  assets/                        Plantilla GFPI-F-135
pruebas/                         JSON de prueba (guía, instrumentos, planeación, juicios)
```

## Comandos
```bash
pip install pdfplumber
python skills/guia-aprendizaje-sena/scripts/buscar_programa.py --buscar "software"
python skills/guia-aprendizaje-sena/scripts/extraer_estructura.py <carpeta_pdfs> --salida skills/guia-aprendizaje-sena/data/programas
python skills/guia-aprendizaje-sena/scripts/extraer_proyecto.py ../proyectos-formativos --salida skills/guia-aprendizaje-sena/data/proyectos
python skills/guia-aprendizaje-sena/scripts/buscar_proyecto.py --programa 228118
python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos datos.json --programa skills/guia-aprendizaje-sena/data/programas/228118_v1.json
python skills/guia-aprendizaje-sena/scripts/generar_guia.py --datos datos.json --salida salidas/guia.docx
python skills/guia-aprendizaje-sena/scripts/generar_instrumentos.py --datos instrumentos.json --salida salidas/instrumentos.docx
python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos datos.json --instrumentos instrumentos.json --programa <programa.json>
python skills/planeacion-pedagogica-sena/scripts/generar_planeacion.py --datos pruebas/planeacion_adso_ap3.json --salida salidas/planeacion.xlsx
python skills/planeacion-pedagogica-sena/scripts/validar_planeacion.py --datos pruebas/planeacion_adso_ap3.json --proyecto skills/guia-aprendizaje-sena/data/proyectos/2480542.json --xlsx salidas/planeacion.xlsx
python skills/juicios-evaluativos-sena/scripts/consolidar_juicios.py --datos pruebas/juicios_adso_ficha_prueba.json --salida salidas/juicios.xlsx --planes salidas/planes.json
python skills/juicios-evaluativos-sena/scripts/generar_plan_mejoramiento.py --datos salidas/planes.json --salida salidas/planes.docx
```

## Empaquetar
`python empaquetar.py` regenera las plantillas incrustadas y genera en `../entregables` un `.skill` y un `-skill.zip` por skill y el plugin `.zip` (ChatGPT); actualiza `dist/`. Ejecútelo tras cambiar la skill o el catálogo.

## Instalación
**Claude Code** (plugin)
```
/plugin marketplace add oyanguas82/fpi-sena-skill
/plugin install fpi-sena@fpi-sena-marketplace
```
En la app de escritorio: Agregar marketplace → `https://github.com/oyanguas82/fpi-sena-skill.git` → Sincronizar → instalar **fpi-sena**.

**Actualizar en Claude Code / app de escritorio.** Los marketplaces de terceros no se actualizan solos: el botón «Actualizar» del plugin compara contra la copia local del marketplace. Primero refresque el marketplace y luego el plugin:
- App de escritorio: sección de marketplaces → `fpi-sena-marketplace` → **Sincronizar / Actualizar marketplace** (o active la actualización automática). Si sigue en una versión vieja, quite el marketplace, vuelva a agregarlo y reinstale **fpi-sena**.
- Terminal: `claude plugin marketplace update fpi-sena-marketplace` y luego `claude plugin update fpi-sena@fpi-sena-marketplace`; o en una sesión `/plugin` → Marketplaces → `fpi-sena-marketplace` → **Update marketplace** / **Enable auto-update**.

**Codex** (plugin)
```
codex plugin marketplace add oyanguas82/fpi-sena-skill
```
Luego instale **fpi-sena** desde el directorio de plugins (app de escritorio de ChatGPT/Codex).

**Claude (claude.ai web/escritorio)** (skills): descargue [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) (obligatoria) y las que necesite de `dist/` (`planeacion-pedagogica-sena`, `instrumentos-evaluacion-sena`, `juicios-evaluativos-sena`, `asistente-fpi-sena`); súbalas en Configuración › Capacidades › Skills. Requiere ejecución de código.

**ChatGPT** — hay dos archivos distintos según la opción que use:
| Opción en ChatGPT | Archivo | Contenido |
|---|---|---|
| **Complementos / Plugins** → subir plugin | [`dist/fpi-sena-plugin-chatgpt.zip`](dist/fpi-sena-plugin-chatgpt.zip) | `plugin.json` y `.codex-plugin/plugin.json` en la raíz, `skills/`, `assets/` |
| **Plugins › Skills** → Create → Upload from your computer | [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) | carpeta `guia-aprendizaje-sena/` con `SKILL.md` |

Si sube el ZIP de la skill por «Complementos», ChatGPT responde *Expected a single plugin archive*: use el ZIP del plugin.

**GPT personalizado (recomendado en ChatGPT, se comparte con un enlace):** Explorar GPTs › Crear › Configurar: pegue [`docs/gpt-instrucciones.md`](docs/gpt-instrucciones.md) en Instrucciones, suba `dist/fpi-sena-plugin-chatgpt.zip` en Conocimiento y active Intérprete de código y análisis de datos. Los archivos de Conocimiento sí quedan en el Python del GPT (`/mnt/data`), así que genera todo sin pedir nada.

**Archivos oficiales en ChatGPT (una sola vez):** el Python de ChatGPT no siempre recibe los scripts del complemento. Cree un **Proyecto** en ChatGPT y suba `dist/fpi-sena-plugin-chatgpt.zip` en **Archivos del proyecto**; desde los chats de ese Proyecto el agente encuentra y extrae el paquete solo (bloque «Ubicar el paquete» de cada `SKILL.md`) y genera guía, planeación, instrumentos, juicios y planes con las plantillas institucionales, sin pedir nada. Requiere la ejecución de código (análisis de datos) activada.

Pasos de prueba en [docs/PRUEBAS.md](docs/PRUEBAS.md).

## Licencia
Código y documentación propios: [MIT](LICENSE). Las plantillas GFPI-F-135 y GFPI-F-134, el logo SENA, el catálogo curricular y los resúmenes de obras de terceros no están cubiertos: ver [NOTICE.md](NOTICE.md).
