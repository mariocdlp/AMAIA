---
name: propuesta
description: Genera una propuesta de automatización profesional para AMAIA en Google Docs. Conversa con el usuario para entender el proyecto, decide qué secciones aplican, arma el HTML con branding AMAIA y lo sube a la carpeta "Clientes" del Drive del usuario. Invocar cuando el usuario diga "/propuesta", "armar propuesta", "nueva propuesta para <cliente>" o similar.
---

# Skill: Propuesta AMAIA

Tu trabajo es producir un Google Doc con una propuesta de automatización detallada para un cliente de AMAIA. El doc final debe transmitir la profundidad del trabajo y elevar el valor percibido — los ejemplos que el usuario tomó de referencia tienen 4-8 páginas con secciones muy específicas (pipelines numerados, workflows con triggers/acciones/exit conditions, forms con campos exactos, timeline por fases, pricing detallado).

## Flujo de la conversación

### 1. Briefing inicial
Si el usuario ya describió el proyecto, no le pidas que repita lo que ya dijo. Si arrancó con un mensaje corto ("propuesta para X"), pedile el brief en una sola tanda con una pregunta abierta:

> Contame lo siguiente, todo lo que sepas (lo que falte lo completamos después):
> 1. **Cliente**: nombre, industria, tamaño, ubicación.
> 2. **Problema/contexto**: qué pasa hoy que no les gusta o qué quieren mejorar.
> 3. **Objetivos**: qué resultados esperan (más leads, menos tiempo, mejor conversión, etc.).
> 4. **Alcance**: qué procesos o canales toca la automatización (ventas, atención, agendamiento, cobros, post-venta, etc.).
> 5. **Stack actual**: herramientas que usan (CRM, calendario, telefonía, pagos, ads, web).
> 6. **Integraciones específicas** que tengan que sí o sí estar.
> 7. **Timeline** deseado y **presupuesto** (si lo tienen definido).
> 8. **Diferenciales** o cualquier nota de tono/marca para incluir.

### 2. Completar info faltante
Después del brief, identificá qué falta para producir un doc convincente. Hacé preguntas SOLO sobre lo que realmente bloquea la calidad del entregable. No pidas datos que podés inferir o asumir razonablemente. Si algo es técnico y opcional, marcalo como "asumido — ajustar si difiere" en el doc en lugar de bloquear al usuario con preguntas.

Datos que típicamente sí necesitás confirmar:
- Nombre exacto del cliente (para el título del doc)
- Pricing total y desglose (a menos que el usuario haya dicho "vos decidí")
- Si hay integraciones inusuales o stack desconocido

Datos que NO debés preguntar (inferí o redactá vos):
- Nombres de pipelines, etapas, workflows internos
- Cantidad de campos en formularios
- Texto de mensajes de seguimiento
- Wording de objetivos y outcomes

### 3. Decidir secciones (estructura adaptable)
La estructura es **adaptable por proyecto**. Incluí solo las secciones que aporten valor real al cliente. Guía:

| Sección | Cuándo incluirla |
|---|---|
| **Goals & Outcomes** | Siempre. |
| **Challenges** | Si el proyecto tiene riesgos operativos no triviales. |
| **Customer Journey / Pipelines** | Si hay flujo de leads, clientes o tickets con múltiples estados. |
| **Funnels & Websites** | Si hay landings, captura web o booking pages embebidos. |
| **Forms & Surveys** | Si hay captura estructurada de datos (intake, feedback, qualification). |
| **Workflows & Automation** | Casi siempre. Es el corazón del entregable. |
| **Calendars** | Si hay agendamiento de citas o asignación de slots. |
| **AI Agents / Chatbot** | Si parte del flujo es conversacional con IA. |
| **Integrations** | Siempre que haya 1+ integración con stack del cliente. |
| **Reporting & Dashboards** | Si el cliente pidió métricas o el caso lo amerita. |
| **Timeline** | Siempre. Adaptá las fases al alcance real. |
| **Pricing** | Siempre, salvo que el usuario diga explícitamente que no lo incluyas. |
| **Soporte & Mantenimiento** | Siempre. |

### 4. Generar el HTML
Usá el archivo `template.html` de este mismo skill como referencia visual y de estructura. Construí el HTML completo en memoria (no lo escribas a disco) siguiendo estas reglas:

- **Encoding**: UTF-8.
- **Estilos inline o en `<style>`**: Google Docs ignora la mayoría de CSS al importar pero respeta `<h1>`, `<h2>`, `<h3>`, `<strong>`, `<em>`, `<ul>`, `<ol>`, `<table>`, `<blockquote>`. Usá esa jerarquía para que se vea bien.
- **Títulos**: `<h1>` para el título principal ("Propuesta de Automatización — \<Cliente\>"), `<h2>` para secciones, `<h3>` para subsecciones (cada pipeline, cada workflow, cada form).
- **Pipelines y workflows**: numerados (`001. Nombre`, `002. Nombre`...) con triggers, goal, acciones (lista), exit conditions cuando aplique.
- **Forms**: lista de campos con tipo entre paréntesis (`Email (Email)`, `Roof Age (Dropdown: <5, 5-10, 10-20, >20)`).
- **Tablas**: usalas para pricing, timeline por fases, matriz de integraciones.
- **Tono**: profesional, en español rioplatense neutro a menos que el cliente sea de otro mercado. Específico, no genérico. Si una sección termina sonando como bullet points genéricos de IA, reescribila con detalles del proyecto.
- **Largo objetivo**: 4-10 páginas. La densidad de los ejemplos de referencia es la vara.
- **Branding AMAIA**: header con "AMAIA — Automatización Inteligente" y footer con datos de contacto del usuario si los proveyó (si no, omitir).

### 5. Crear el Google Doc en Drive
Usá la herramienta `mcp__ae7a3d90-5504-45bb-918e-1adab466b474__create_file` con estos parámetros exactos:

```
title: "Propuesta — <Cliente> — <YYYY-MM-DD>"
parentId: "1bzguRz9FQeThGj2clnNxv67CIkefCDO9"
contentMimeType: "text/html"
textContent: <el HTML completo>
```

**No** pasés `disableConversionToGoogleType` — queremos que Drive convierta el HTML a Google Doc nativo. **No** pases `mimeType` (está deprecated). Usá la fecha de hoy en el título (formato ISO).

Si el tool retorna error de conversión HTML, fallback:
1. Convertí el HTML a Markdown (preservando headers, listas, tablas).
2. Reintentá con `contentMimeType: "text/markdown"` (Drive importa MD a Google Docs nativamente).
3. Si eso también falla, último recurso: `contentMimeType: "text/plain"` con el contenido en markdown plano (perderá formato visual pero el doc se crea).

### 6. Confirmar al usuario
Devolvé al usuario:
- El **título** del doc creado.
- El **link directo** al doc (la respuesta del tool incluye el ID — construí el URL como `https://docs.google.com/document/d/<id>/edit`).
- Un **resumen breve** (3-5 líneas) de qué secciones incluiste y qué decisiones tomaste (ej: "incluí pipelines pero no funnels porque el flujo es solo telefónico").
- Una **invitación** a iterar: "decime qué ajustar y lo edito en el mismo doc o regenero."

## Reglas duras

- **NO** crees el Doc antes de que el usuario haya confirmado el brief mínimo (cliente + objetivos + alcance). Si el brief está incompleto, pedí lo que falta antes.
- **NO** subas múltiples versiones del doc al Drive en un mismo turno. Una propuesta = un doc.
- **NO** inventes números de pricing si el usuario no los dio. Si no hay precio, dejá la sección con un placeholder claro (`[A definir según alcance final]`) o omitila si el usuario lo pidió.
- **NO** copies frases textuales de los ejemplos del colega. La estructura sí, el wording propio.
- **SÍ** asumí defaults razonables para detalles operativos (cantidad de etapas, nombres de workflows, mensajes de follow-up) y marcalos como editables.
- **SÍ** mantené coherencia: si mencionás "Pipeline 003" en Workflows, debe existir en la sección Pipelines.

## Iteración

Si el usuario pide cambios después de generar el doc, opciones:
1. **Cambios chicos** (corregir nombre, ajustar precio, agregar 1 sección): regenerá el HTML completo y creá un doc nuevo con sufijo `— v2` en el título. No edites el viejo (no hay tool de edición de Google Docs).
2. **Cambios grandes** (reorientar el alcance): proponé regenerar desde cero confirmando el nuevo brief.

Mencioná siempre al usuario que los Google Docs no se pueden editar desde acá — solo crear nuevas versiones.
