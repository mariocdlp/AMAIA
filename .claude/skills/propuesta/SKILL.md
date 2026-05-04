---
name: propuesta
description: Genera una propuesta de automatización profesional para AMAIA en Google Docs. Conversa con el usuario para entender el proyecto, decide qué secciones aplican, arma el HTML con branding AMAIA y lo sube a la carpeta "Clientes" del Drive del usuario. Invocar cuando el usuario diga "/propuesta", "armar propuesta", "nueva propuesta para <cliente>" o similar.
---

# Skill: Propuesta AMAIA

Tu trabajo es producir un Google Doc con una propuesta de automatización detallada para un cliente de AMAIA. El doc final debe transmitir la profundidad del trabajo y elevar el valor percibido — los ejemplos que el usuario tomó de referencia tienen 4-8 páginas con secciones muy específicas (pipelines numerados, workflows con triggers/acciones/exit conditions, forms con campos exactos, timeline por fases, pricing detallado).

## Tech stack de AMAIA (asumir por defecto)

- **HighLevel (GHL)** es la herramienta principal de toda propuesta. Asumí que la cuenta del cliente vive en GHL salvo que el usuario diga lo contrario. Pipelines, contactos, oportunidades, formularios, calendarios, workflows nativos, conversaciones (SMS/Email/WhatsApp/voz), funnels y sitios se construyen ahí.
- **n8n** se usa para todo lo que GHL no puede hacer nativo: integraciones con APIs externas no soportadas, transformaciones complejas de datos, flujos de aprobación con sistemas internos, scraping/enriquecimiento, lógica condicional avanzada, fan-out a múltiples sistemas. Cuando incluyas un workflow de n8n, **siempre justificá por qué no se hace en GHL** ("GHL no soporta X", "se necesita procesamiento batch que GHL no permite", etc.).
- **Stack del cliente**: cualquier herramienta que el cliente ya use o pida (CRM legacy, telefonía, pasarela de pago, ERP, agendamiento, BI, etc.) debe quedar reflejada en la sección de Integraciones, especificando si se conecta vía nativo de GHL, API directa de GHL, o n8n como puente.

Si el usuario no menciona el stack del cliente en el brief, preguntá explícitamente: "¿qué herramientas usa hoy el cliente que tengamos que integrar?" antes de generar el doc.

## Flujo de la conversación

### 1. Briefing inicial
Si el usuario ya describió el proyecto, no le pidas que repita lo que ya dijo. Si arrancó con un mensaje corto ("propuesta para X"), pedile el brief en una sola tanda con una pregunta abierta:

> Contame lo siguiente, todo lo que sepas (lo que falte lo completamos después):
> 1. **Cliente**: nombre, industria, tamaño, ubicación.
> 2. **Problema/contexto**: qué pasa hoy que no les gusta o qué quieren mejorar.
> 3. **Objetivos**: qué resultados esperan (más leads, menos tiempo, mejor conversión, etc.).
> 4. **Alcance**: qué procesos o canales toca la automatización (ventas, atención, agendamiento, cobros, post-venta, etc.).
> 5. **Stack actual del cliente**: herramientas que ya usan y queremos integrar (telefonía, pagos, ads, web, CRM legacy si están migrando, ERP, agendamiento externo, etc.). El stack base de AMAIA es **GHL + n8n** — eso ya lo asumo.
> 6. **Integraciones específicas** que tengan que sí o sí estar, y procesos que claramente no se resuelven en GHL (ahí pongo n8n).
> 7. **Timeline** deseado y **presupuesto** (si lo tienen definido).
> 8. **Diferenciales** o cualquier nota de tono/marca para incluir.

### 2. Completar info faltante
Después del brief, identificá qué falta para producir un doc convincente. Hacé preguntas SOLO sobre lo que realmente bloquea la calidad del entregable. No pidas datos que podés inferir o asumir razonablemente. Si algo es técnico y opcional, marcalo como "asumido — ajustar si difiere" en el doc en lugar de bloquear al usuario con preguntas.

Datos que típicamente sí necesitás confirmar:
- Nombre exacto del cliente (para el título del doc)
- Pricing total y desglose (a menos que el usuario haya dicho "vos decidí")
- Stack que ya usa el cliente (para integraciones)
- Si hay procesos que requieren claramente n8n (lógica que GHL no resuelve)
- Volumen aproximado (leads/mes, contactos esperados) — impacta A2P, n8n hosting, y pricing

Datos que NO debés preguntar (inferí o redactá vos):
- Nombres de pipelines, etapas, workflows internos
- Custom fields exactos a crear (proponé el set completo, marcalo como "propuesto, ajustable")
- API keys / slugs de custom fields (generá vos en snake_case desde el nombre)
- Convención de naming de tags
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
| **Plan de Build en GHL** | **Siempre** — ver formato detallado abajo. |
| **Workflows complementarios en n8n** | Si hay flujos que GHL no puede resolver nativo. |
| **Integrations** | Siempre que haya 1+ integración con stack del cliente. |
| **Reporting & Dashboards** | Si el cliente pidió métricas o el caso lo amerita. |
| **Timeline** | Siempre. Adaptá las fases al alcance real. |
| **Pricing** | Siempre, salvo que el usuario diga explícitamente que no lo incluyas. |
| **Soporte & Mantenimiento** | Siempre. |

### Plan de Build en GHL (obligatorio, alto detalle)

Esta sección es la que más eleva el valor percibido — el cliente ve exactamente qué se va a configurar en su sub-cuenta de GHL. Incluí estos sub-bloques cuando apliquen, con tablas concretas:

1. **Custom Fields — Contact**
   Tabla con columnas: `Nombre del campo` · `API key (slug)` · `Tipo` · `Grupo/Folder` · `Opciones (si Dropdown/Multi)` · `Required` · `Propósito`.
   Tipos válidos GHL: Text, Large Text, Number, Phone, Email, Date, Dropdown (Single), Dropdown (Multi), Checkbox, Radio, File Upload, Textbox List, Monetary, Signature.

2. **Custom Fields — Opportunity**
   Misma tabla pero para opportunities. Cada pipeline puede tener sus campos.

3. **Custom Values (account-level)**
   Variables que se reutilizan en mensajes/workflows: link de booking, número de WhatsApp, nombre del comercio, link de pago, etc. Tabla: `Nombre` · `Valor sugerido` · `Dónde se usa`.

4. **Tags (convención de naming)**
   Listá los tags con convención consistente (ej: `lead-source-google`, `qualified`, `nurture-30d`, `dbr-triggered`). Tabla: `Tag` · `Cuándo se asigna` · `Cuándo se remueve`.

5. **Pipelines + Stages**
   Para cada pipeline: nombre, cantidad de stages, lista numerada de stages con goal de cada uno (esto puede solaparse con la sección Customer Journey — si la incluiste arriba, acá podés referenciarla y solo agregar el detalle técnico de orden y triggers de cambio de stage).

6. **Forms & Surveys (GHL)**
   Si ya tenés sección de Forms arriba, acá solo el detalle de implementación: en qué embed/funnel/standalone va cada uno, redirect post-submit, workflow disparado.

7. **Calendars (GHL)**
   Tipo (Round Robin / Class / Collective / Service), team members, slot duration, buffer, working hours, form de booking asociado, custom fields del booking, confirmation/reminder workflows.

8. **Workflows nativos GHL**
   Para cada uno: nombre, trigger (event-based, contact tag, form submit, appointment, pipeline stage change, etc.), pasos numerados (Send SMS, Send Email, If/Else, Wait, Update Field, Add Tag, Remove Tag, Create Opportunity, Move to Stage, Webhook, Math, etc.), exit conditions.

9. **Triggers links / Snapshot items**
   Si hay trigger links (clicks que disparan workflows), listalos. Si la entrega incluye un snapshot exportable, mencionalo.

10. **Conversaciones — Templates**
    SMS, Email (subject + preview), WhatsApp templates si aplica. Para cada uno: nombre del template, canal, momento del journey en que se envía, cuerpo (puede ser sample, no literal).

11. **Memberships / Funnels / Websites**
    Solo si aplica. Páginas a construir, formularios embebidos, dominio.

12. **Sub-cuenta y configuración inicial**
    Bullet list: creación de sub-account, branding (logo, colores), dominio custom, A2P registration (US), número(s) telefónico(s) a provisionar, SMTP/email sending domain, integraciones nativas a conectar (Google, Facebook, Stripe, etc.), users/roles internos del cliente.

### Workflows complementarios en n8n (cuando aplique)

Para cada workflow n8n incluí: `Nombre` · `Trigger` (webhook desde GHL / cron / evento externo) · `Nodos principales` (numerados con la lógica) · `Sistemas que toca` · `Por qué no se hace nativo en GHL` · `Manejo de errores` (retry, alerta a Slack/email, logging). Mencioná dónde se hostea n8n (cloud propio de AMAIA o instancia del cliente).

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
- **SÍ** mantené coherencia: si mencionás "Pipeline 003" en Workflows, debe existir en la sección Pipelines. Si un workflow lee/escribe un custom field, ese campo debe figurar en el Plan de Build en GHL. Si referenciás un custom value (ej: `{{custom_values.booking_link}}`), declaralo en la tabla de Custom Values.
- **SÍ** marcá explícitamente cada automatización como `[GHL nativo]` o `[n8n]` en la sección de Workflows. Si está en n8n, la justificación de por qué no se hace en GHL debe ser clara.

## Iteración

Si el usuario pide cambios después de generar el doc, opciones:
1. **Cambios chicos** (corregir nombre, ajustar precio, agregar 1 sección): regenerá el HTML completo y creá un doc nuevo con sufijo `— v2` en el título. No edites el viejo (no hay tool de edición de Google Docs).
2. **Cambios grandes** (reorientar el alcance): proponé regenerar desde cero confirmando el nuevo brief.

Mencioná siempre al usuario que los Google Docs no se pueden editar desde acá — solo crear nuevas versiones.
