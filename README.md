# AMAIA — Automation Proposals

Repositorio de utilidades de Claude Code para AMAIA, una agencia de automatización.

## Skill: `/propuesta`

Genera una propuesta de automatización profesional en Google Docs a partir de un brief conversacional.

### Cómo usarlo

1. Abrí Claude Code en este repo.
2. Escribí `/propuesta` o algo como "armar propuesta para `<cliente>`".
3. El skill te va a pedir un brief (cliente, problema, objetivos, alcance, stack, integraciones, timeline, presupuesto, diferenciales).
4. Si falta algo crítico te pregunta lo mínimo para no bloquear.
5. Genera el HTML con secciones adaptadas al proyecto (incluye solo las que aplican: pipelines, funnels, forms, workflows, calendarios, agentes de IA, integraciones, reporting, timeline, pricing, soporte).
6. Sube el doc a la carpeta **Clientes** de tu Drive (folder ID `1bzguRz9FQeThGj2clnNxv67CIkefCDO9`) y te devuelve el link.

### Estructura

```
.claude/skills/propuesta/
├── SKILL.md         # instrucciones que sigue Claude
└── template.html    # plantilla de referencia con todas las secciones posibles
```

### Iteración

Los Google Docs no se editan desde acá — para cambios se genera una nueva versión (`v2`, `v3`...) en la misma carpeta.

### Cambiar la carpeta destino

Editá el `parentId` en `.claude/skills/propuesta/SKILL.md` (sección "Crear el Google Doc en Drive").
