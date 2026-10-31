# FPI SENA – Skill de Guías de Aprendizaje (GFPI-F-135 V04)

Skill (estándar SKILL.md) para Claude, Claude Code, Codex y ChatGPT que diseña guías de aprendizaje SENA en Word a partir de la estructura curricular oficial.

## Estructura
```
plugin.json                      Manifiesto del plugin (Codex / ChatGPT, formato portátil)
.codex-plugin/plugin.json        Manifiesto Codex (compatibilidad)
.agents/plugins/marketplace.json Marketplace para Codex / ChatGPT
.claude-plugin/                  Plugin y marketplace para Claude Code
dist/                            Skill (.zip, claude.ai y ChatGPT › Skills) y plugin (.zip, ChatGPT › Complementos)
skills/guia-aprendizaje-sena/
  SKILL.md                       Instrucciones y flujo
  references/                    Reglas del formato, evaluación, estrategias, Bloom, APA
  scripts/                       generar_guia, generar_instrumentos, validar_guia, buscar_programa, buscar_proyecto, extraer_estructura, extraer_proyecto
  data/                          Catálogo curricular (68 programas) y proyectos formativos (37)
  assets/                        Plantilla GFPI-F-135
pruebas/                         JSON de prueba (guía e instrumentos)
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
```

## Empaquetar
`python empaquetar.py` genera en `../entregables` el `.skill` (Claude), la skill `.zip` y el plugin `.zip` (ChatGPT), y actualiza `dist/` con la skill y el plugin. Ejecútelo tras cambiar la skill o el catálogo.

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

**Claude (claude.ai web/escritorio)** (skill): descargue [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) y súbalo en Configuración › Capacidades › Skills. Requiere ejecución de código.

**ChatGPT** — hay dos archivos distintos según la opción que use:
| Opción en ChatGPT | Archivo | Contenido |
|---|---|---|
| **Complementos / Plugins** → subir plugin | [`dist/fpi-sena-plugin-chatgpt.zip`](dist/fpi-sena-plugin-chatgpt.zip) | `plugin.json` y `.codex-plugin/plugin.json` en la raíz, `skills/`, `assets/` |
| **Plugins › Skills** → Create → Upload from your computer | [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) | carpeta `guia-aprendizaje-sena/` con `SKILL.md` |

Si sube el ZIP de la skill por «Complementos», ChatGPT responde *Expected a single plugin archive*: use el ZIP del plugin.

**Word con la plantilla oficial en ChatGPT:** la plantilla viaja también incrustada en `scripts/plantilla.py`, así que basta con que ChatGPT ejecute los scripts del complemento; no hace falta adjuntar nada. Requiere la ejecución de código (análisis de datos) activada. Solo si ChatGPT no encuentra ningún script, adjunte [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) en la conversación o en los archivos del Proyecto. La subida de plugins puede requerir permisos de administrador del espacio de trabajo.

Pasos de prueba en [docs/PRUEBAS.md](docs/PRUEBAS.md).

## Licencia
Código y documentación propios: [MIT](LICENSE). La plantilla GFPI-F-135, el logo SENA, el catálogo curricular y los resúmenes de obras de terceros no están cubiertos: ver [NOTICE.md](NOTICE.md).
