# Plan de trabajo base — AMAIA

Wording, defaults y convenciones que el skill `/propuesta` debe **reutilizar** siempre que apliquen al proyecto, en lugar de inventar nuevos. Si un bloque acá encaja con el caso del cliente, copialo (ajustando duraciones, nombres y montos) en vez de redactar uno desde cero.

> **Perspectiva**: AMAIA construye **directamente sobre la sub-cuenta de GHL del cliente final**. La sub-cuenta es el entregable. **No** hablar de "cuenta maestra", "agencia", "white-label", ni "snapshot". El cliente es un negocio operativo (no una agencia que revende).

---

## Convenciones de naming

- **Pipelines stages**: numerar `001`, `002`, `003`... con descripción corta en mayúscula inicial. Emoji 🤖 al final del nombre cuando una etapa es manejada por IA.
- **Workflows**: prefijo `A` + número de tres dígitos (`A001`, `A002`...). Mantener correspondencia 1:1 con etapas del pipeline cuando aplique.
- **API keys de custom fields**: snake_case en español del nombre del campo. Ej: "Edad del techo" → `edad_del_techo`.
- **Custom values**: snake_case con prefijo de área. Ej: `booking_link`, `wapp_business`, `nombre_comercio`.
- **Tags**: kebab-case con categoría como prefijo. Ej: `lead-source-google`, `qualified`, `nurture-30d`, `dbr-triggered`.

---

## Pipeline base de captación (adaptable)

Cuando el proyecto incluye captación → cierre, partir de estas etapas y ajustar nombres a la industria:

```
001. Nuevo Lead 🤖
002. Cita Agendada
003. No se Presentó
004. Seguimiento / Nutrición
005. Ganado
```

Para flujos más completos (ventas + entrega + reseñas), expandir con etapas tipo `006. Servicio Entregado`, `007. Solicitud de Reseña`, `008. Reseña Recibida`.

---

## Funnels base (cuando aplica web/captura)

- **Landing Page** — captura con CTA principal del proyecto.
- **Página de Auto-Agendamiento** — calendario embebido para que el lead reserve solo.
- **Página de Confirmación de Cita** — agradecimiento + próximos pasos.
- **Página de Solicitud de Reseña** — links directos a Google/Facebook + lógica de filtro de feedback negativo.

Solo incluir los que apliquen al proyecto.

---

## Workflows base (cuando aplica el flujo)

| ID | Nombre | Trigger | Acción principal |
|---|---|---|---|
| A001 | Nutrición de Nuevo Lead | Form submit en Landing | Crear contacto, mover a `001 Nuevo Lead`, secuencia Email/SMS hacia agendamiento |
| A002 | Agendamiento y Recordatorios | Cita agendada en calendario | Mover a `002 Cita Agendada`, confirmación + recordatorios 24h/1h/15min |
| A003 | Seguimiento No-Show / Cancelado | Cita marcada no-show o cancelada | Mover a `003 No se Presentó`, secuencia de re-agendamiento |
| A004 | Pago y Onboarding | Pago recibido | Mover a `005 Ganado`, email de bienvenida, notificar al equipo |
| A005 | Solicitud de Reseña | Lead movido a "Servicio Entregado" | Secuencia post-entrega con filtro: 5★ → Google, <4★ → privado |

Adaptar/agregar según alcance. Mantener la convención de prefijo `A` + número.

---

## Herramientas de GHL utilizadas (mencionar las que aplican)

- **Funnels & Sites** — para landings, páginas de booking y de confirmación.
- **Calendars** — para gestión de citas (Round Robin / Service / Class según caso).
- **Workflows** — automatización nativa de comunicación y procesos.
- **Forms & Surveys** — captura de leads y datos de onboarding.
- **Email & SMS / WhatsApp Marketing** — secuencias de nutrición, recordatorios, follow-up.
- **Payments** — Stripe / PayPal / Mercado Pago para checkout y facturación.
- **CRM Pipelines** — visualización del flujo de oportunidades.
- **Conversation AI / Voice AI** — agente conversacional para texto y llamadas.
- **Reputation Management** — gestión y solicitud centralizada de reseñas.

---

## Cronograma estándar (Timeline)

Cinco fases. Ajustar duraciones según alcance real. Si el alcance es chico, comprimir Fase 2 a 1-2 semanas; si es grande, hasta 4-5.

### Fase 1 — Descubrimiento y Estrategia
**Duración**: 1 semana.
**Actividades**: Reunión inicial para alinear visión y criterios de éxito. Acceso a herramientas actuales del cliente. Recopilación de branding (logo, colores, dominios) y textos para embudos/mensajes. Definición fina de pipelines, custom fields y workflows del alcance.

### Fase 2 — Construcción y Personalización
**Duración**: 2-3 semanas (ajustar al alcance).
**Actividades**: Build completo en la sub-cuenta del cliente — pipelines, custom fields y custom values, tags, formularios, calendarios, workflows nativos, funnels/sitios, integraciones, agentes de IA. Configuración de mensajería (SMS/Email/WhatsApp) y plantillas. Si aplica, construcción de workflows complementarios en n8n.

### Fase 3 — Pruebas y Retroalimentación
**Duración**: 1 semana.
**Actividades**: Pruebas internas end-to-end de cada flujo. Entrega de un entorno funcional para revisión del cliente. Aplicación de ajustes según feedback.

### Fase 4 — Capacitación y Entrega
**Duración**: 1 semana.
**Actividades**: Sesión(es) de capacitación con el equipo del cliente para uso de la plataforma, lectura del CRM, manejo de oportunidades, conversaciones y respuestas. Entrega de documentación operativa.

### Fase 5 — Soporte Post-Implementación
**Duración**: Según se acuerde (típicamente 2-4 semanas incluidas en el proyecto).
**Actividades**: Soporte para resolver dudas o ajustes técnicos en las primeras semanas de operación. Pasada esta fase, continúa el plan de soporte mensual.

---

## Soporte y Mantenimiento (Managed Services)

Bloque de wording listo para reutilizar en la sección de Soporte de la propuesta.

### Resumen
Tras la entrega inicial, AMAIA ofrece un servicio de gestión continua que libera al cliente de las operaciones técnicas diarias de la plataforma. El equipo de AMAIA actúa como brazo técnico y de soporte, permitiendo al cliente enfocarse en su operación comercial.

### Servicios incluidos (dentro del alcance mensual)

**Mantenimiento técnico**
- Monitoreo del funcionamiento de pipelines, workflows e integraciones.
- Diagnóstico y resolución de problemas técnicos (workflows que no se disparan, formularios que fallan, integraciones rotas, etc.).
- Mantenimiento frente a actualizaciones de GHL y proveedores integrados.

**Soporte continuo**
- Canal de tickets centralizado para reportar incidencias.
- Sesiones grupales periódicas (semanales o quincenales, según paquete) con resolución de dudas, mejores prácticas y novedades de la plataforma.
- Hasta `{{N}}` horas mensuales de cambios menores (ajuste de mensajes, agregado de campos simples, edición de templates, etc.).

**Onboarding y configuración (si el cliente suma usuarios o áreas nuevas dentro de la sub-cuenta)**
- Configuración inicial de los nuevos componentes en la sub-cuenta existente.
- Conexión de cuentas adicionales (redes sociales, calendarios, números telefónicos).
- Una sesión de onboarding 1-a-1 de hasta 60 minutos por cada nueva área/usuario que se sume.

### Servicios excluidos (fuera de alcance)

- **Soporte 1-a-1 individualizado** más allá de la sesión de onboarding inicial. Las consultas se canalizan vía tickets o sesiones grupales.
- **Gestión de campañas de marketing** (Facebook Ads, Google Ads, etc.).
- **Creación de contenido o copy** (textos publicitarios, diseño, video, redacción de emails/posts).
- **Gestión de leads y conversaciones**: AMAIA no interactúa con los leads del cliente. Contactar, calificar y cerrar ventas es responsabilidad del cliente.
- **Desarrollos a medida** (nuevos funnels complejos, workflows extensos, integraciones con software no nativo, código CSS/JS personalizado). Se cotizan aparte.
- **Resultados de negocio**: AMAIA no garantiza número de leads, ventas o reseñas — dependen de factores fuera del control técnico (oferta, presupuesto de ads, capacidad de cierre del cliente).

### SLA y operación

- **Canal**: portal de tickets / email de soporte (a definir).
- **Horario**: Lunes a Viernes, 9:00 a 18:00 (zona horaria del cliente).
- **Tiempos de primera respuesta**:
  - Crítico (plataforma caída): menos de 4 horas hábiles.
  - Técnico general: menos de 24 horas hábiles.
  - Consultas generales: menos de 48 horas hábiles.
- **Sesiones grupales**: día y hora a confirmar; grabaciones disponibles.

---

## Pricing — defaults

Si el usuario no especifica precio, asumir esquema:

- **Proyecto inicial**: 50% al inicio, 40% al finalizar testing/feedback, 10% en capacitación e implementación.
- **Soporte mensual**: cuota recurrente con compromiso mínimo de 3 meses.

Si el usuario dice "vos decidí" sobre el precio, proponer un rango basado en cantidad de pipelines, workflows, agentes de IA e integraciones, y dejar claro que es un estimado a confirmar tras Fase 1.

Si el usuario no da precio ni autoriza estimar, dejar la sección con `[A definir tras Fase 1 de Descubrimiento]` en lugar de inventar números.
