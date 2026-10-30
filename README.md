# FPI SENA – Skill de Guías de Aprendizaje (GFPI-F-135 V04)

Skill (estándar SKILL.md) para Claude, Claude Code, Codex y ChatGPT que diseña guías de aprendizaje SENA en Word a partir de la estructura curricular oficial.

## Estructura
```
plugin.json                      Manifiesto del plugin (Codex / ChatGPT, formato portátil)
.codex-plugin/plugin.json        Manifiesto Codex (compatibilidad)
.agents/plugins/marketplace.json Marketplace para Codex / ChatGPT
.claude-plugin/                  Plugin y marketplace para Claude Code
dist/                            Skill empaquetada (.zip) para claude.ai y ChatGPT
skills/guia-aprendizaje-sena/
  SKILL.md                       Instrucciones y flujo
  references/                    Reglas del formato, evaluación, estrategias, Bloom, APA
  scripts/                       generar_guia, generar_instrumentos, validar_guia, buscar_programa, extraer_estructura
  data/                          Catálogo curricular (68 programas)
  assets/                        Plantilla GFPI-F-135
pruebas/                         JSON de prueba (guía e instrumentos)
```

## Comandos
```bash
pip install pdfplumber
python skills/guia-aprendizaje-sena/scripts/buscar_programa.py --buscar "software"
python skills/guia-aprendizaje-sena/scripts/extraer_estructura.py <carpeta_pdfs> --salida skills/guia-aprendizaje-sena/data/programas
python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos datos.json --programa skills/guia-aprendizaje-sena/data/programas/228118_v1.json
python skills/guia-aprendizaje-sena/scripts/generar_guia.py --datos datos.json --salida salidas/guia.docx
python skills/guia-aprendizaje-sena/scripts/generar_instrumentos.py --datos instrumentos.json --salida salidas/instrumentos.docx
python skills/guia-aprendizaje-sena/scripts/validar_guia.py --datos datos.json --instrumentos instrumentos.json --programa <programa.json>
```

## Empaquetar
`python empaquetar.py` genera en `../entregables` el `.skill` (Claude), la skill `.zip` (ChatGPT) y el plugin `.zip`, y actualiza `dist/guia-aprendizaje-sena-skill.zip`. Ejecútelo tras cambiar la skill o el catálogo.

## Instalación
**Claude Code** (plugin)
```
/plugin marketplace add oyanguas82/fpi-sena-skill
/plugin install fpi-sena@fpi-sena-marketplace
```
En la app de escritorio: Agregar marketplace → `https://github.com/oyanguas82/fpi-sena-skill.git` → Sincronizar → instalar **fpi-sena**.

**Codex** (plugin)
```
codex plugin marketplace add oyanguas82/fpi-sena-skill
```
Luego instale **fpi-sena** desde el directorio de plugins (app de escritorio de ChatGPT/Codex).

**Claude (claude.ai web/escritorio)** (skill): descargue [`dist/guia-aprendizaje-sena-skill.zip`](dist/guia-aprendizaje-sena-skill.zip) y súbalo en Configuración › Capacidades › Skills. Requiere ejecución de código.

**ChatGPT** (skill): Plugins › Skills › Create › Upload from your computer › `dist/guia-aprendizaje-sena-skill.zip` (planes Business, Enterprise, Edu). Como plugin, un administrador sube `fpi-sena-plugin-chatgpt.zip` en Admin console › Plugins.

Pasos de prueba en [docs/PRUEBAS.md](docs/PRUEBAS.md).

## Licencia
Código y documentación propios: [MIT](LICENSE). La plantilla GFPI-F-135, el logo SENA, el catálogo curricular y los resúmenes de obras de terceros no están cubiertos: ver [NOTICE.md](NOTICE.md).
