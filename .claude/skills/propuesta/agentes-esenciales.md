# Catálogo de Agentes Esenciales — AMAIA

Cuando el proyecto incluye automatización conversacional o de voz, identificá cuál(es) de estos agentes aplica y **copiá la descripción canónica** en la sección "Agentes de IA" de la propuesta. Si ninguno encaja exactamente, usalos como base y ajustá; mencioná que es una variante de un agente esencial AMAIA.

Cada agente se construye sobre GHL (Conversation AI / Voice AI) más, cuando aplique, lógica complementaria en n8n.

---

## 1. Agente Chatbot Conversacional

**Canales**: WhatsApp, Facebook Messenger, Instagram DM, chat web.
**Disponibilidad**: 24/7.

**Capacidades**:
- Responde mensajes al instante en todos los canales conectados.
- Atiende prospectos de campañas (ads, orgánico) sin demora.
- Responde preguntas sobre el negocio (servicios, precios, ubicación, horarios).
- Está entrenado para guiar al prospecto hacia un siguiente paso concreto: agendar cita, descargar lead magnet, dejar datos de contacto, etc.
- Consulta y agenda citas en el calendario del negocio.
  - Envía confirmación de cita y recordatorios automáticos.
  - Intenta recuperar citas de ausentismos y cancelaciones.
  - Gestiona la agenda evitando conflictos.
- Canaliza al humano las solicitudes que no puede resolver, con contexto.

**Cuándo proponerlo**: el cliente recibe consultas por WhatsApp/redes y se le escapan o demora la respuesta.

---

## 2. Agente Recepcionista Telefónica

**Canal**: llamadas telefónicas entrantes.
**Disponibilidad**: 24/7 o solo fuera de horario, según configuración.

**Capacidades**:
- Atiende el teléfono cuando no hay nadie disponible (turnos desatendidos, horario fuera de oficina).
- Recopila información del llamante y toma mensajes.
- Puede transferir llamadas siguiendo reglas claras (por ejemplo: emergencia → móvil del dueño; venta → equipo comercial).
- Fácil de entrenar con guion y FAQs del negocio.
- Envía un email con la transcripción completa de la llamada al equipo después de cada interacción.
- Canaliza al humano las solicitudes complejas o sensibles.

**Argumento comercial**: "Con que rescate una venta ya se pagó sola."

**Cuándo proponerlo**: el cliente pierde llamadas en horario, después de hora, o cuando el equipo está ocupado. Industrias típicas: clínicas, talleres, contratistas, servicios profesionales.

---

## 3. Agente de Reactivación de Base de Datos (RBD)

**Canal**: WhatsApp principalmente; SMS/Email como complemento.

**Capacidades**:
- Envía ofertas exclusivas a la base de datos existente del cliente vía WhatsApp.
- Explica la oferta y reserva citas de servicio o de venta directamente desde la conversación.
- Genera facturación desde la primera semana de implementación.
- Conversión promedio observada: 2% a 5% de la base contactada.
- Excelente para reconectar con clientes inactivos y reforzar confianza.

**Cuándo proponerlo**: el cliente tiene una base de datos de contactos inactiva (clientes de hace 6+ meses, leads que no cerraron) y quiere monetizarla rápido.

---

## 4. Agente de Reseñas

**Canal**: SMS, Email, WhatsApp.

**Capacidades**:
- Solicita reseñas a todos los clientes después del servicio.
- Amplifica reseñas positivas (publicación en redes y sitio web).
- Filtra feedback negativo a privado: si la calificación es baja, en lugar de ir a Google va a un canal interno para que el cliente pueda resolver antes de que escale públicamente.
- Responde reseñas siguiendo lineamientos del cliente.
- Publica las mejores reseñas en redes sociales y en el sitio web del cliente.

**Cuándo proponerlo**: el cliente quiere mejorar reputación online (Google, Facebook, Tripadvisor, etc.) y no tiene un proceso sistemático para pedir reseñas.

---

## 5. Agente RBD Reseñas

**Canal**: WhatsApp.
**Combina**: Reactivación de Base de Datos + Solicitud de Reseñas.

**Capacidades**:
- Solicita reseñas a la base de datos histórica del cliente vía WhatsApp.
- Suele generar más reseñas en una semana que las acumuladas en los últimos 3 años.
- Operación 100% ética y legal: solicita explícitamente, no incentiva con dinero, no falsifica.

**Cuándo proponerlo**: el cliente tiene base histórica de clientes satisfechos pero pocas reseñas online; necesita un push masivo en corto plazo.

---

## Cómo presentarlos en la propuesta

- Si el alcance incluye 1-2 agentes, dedicales una sección con descripción y capacidades adaptadas al cliente.
- Si el alcance incluye 3+, agregá una tabla resumen y desarrollá cada uno en sub-secciones.
- Siempre conectá cada agente a:
  - **Workflow GHL** que lo dispara/orquesta.
  - **Custom fields / tags** que actualiza.
  - **Pipeline stage** al que mueve los contactos.
  - **Handoff a humano**: criterio claro de cuándo escala.
