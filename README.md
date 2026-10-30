# FPI SENA – Skill de Guías de Aprendizaje (GFPI-F-135 V04)

Skill (estándar SKILL.md) para Claude y ChatGPT que diseña guías de aprendizaje SENA en Word a partir de la estructura curricular oficial.

## Estructura
```
plugin.json, .codex-plugin/      Manifiestos del plugin ChatGPT
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
`python empaquetar.py` genera ambos paquetes en `../entregables`.
- Claude: comprimir la carpeta `skills/guia-aprendizaje-sena` → `guia-aprendizaje-sena.skill`.
- ChatGPT: comprimir la raíz del repositorio → plugin `.zip`.

## Instalación para otros usuarios
**Claude Code**
```
/plugin marketplace add TU_USUARIO/fpi-sena-skill
/plugin install fpi-sena@fpi-sena-marketplace
```
**Claude (web/escritorio):** descargar `guia-aprendizaje-sena.skill` de Releases y subirlo en Configuración › Skills.
**ChatGPT:** descargar `fpi-sena-plugin-chatgpt.zip` de Releases e instalar el plugin.
