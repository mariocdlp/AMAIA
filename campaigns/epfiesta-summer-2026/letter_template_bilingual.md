# EP Fiesta — Summer 2026 Outreach Letter (Bilingual)

Merge fields used (one per recipient — populated from `mailmerge_contacts.csv`):

| Field | Example |
|---|---|
| `{{title}}` | Abundant Church |
| `{{street}}` | 7100 N Desert Blvd |
| `{{city}}` | El Paso |
| `{{category}}` | Church |
| `{{use_case_en}}` | your summer festivals, outdoor services and family gatherings |
| `{{use_case_es}}` | los festivales de verano, servicios al aire libre y convivencias familiares |

---

## Subject line options (pick one for the A/B)

- **A** — Shade & tents for {{title}}'s next outdoor event
- **B** — A summer favor for {{title}} — 15% off on tents
- **C** — Carpas y sombra para {{title}} — oferta de verano

---

## Letter body — ENGLISH then SPANISH (recipient reads whichever fits)

> Hello {{title}} team,
>
> West Texas summers don't slow down, and neither do the people planning {{use_case_en}} at {{title}}. I'm Mario with **EP Fiesta**, the El Paso tent and party rental company — I'm writing because the events you'll host between now and the holidays are easier (and a lot cooler) when there's real shade over your guests.
>
> We deliver, professionally install and pick up commercial-grade **high-peak frame tents** built for our wind and our sun. Our 20x20 tents are modular, so as your guest list grows, the coverage grows — go from a single 20x20 over the welcome table to a 20x60 over the whole gathering. We also rent **pop-up canopies** for smaller setups, plus **tables, chairs, string lights** and **tent liners** to dress the space up for a wedding-quality look.
>
> **Summer 2026 offer for {{title}}:** book your tent at least **3 months in advance** and we'll take **15% off** your rental. Most {{category}} events that need a tent fall in the back-to-school season and the fall — so locking your date in now gets you both the best price and our first pick of equipment.
>
> Rentals start at **$79**. You can reserve at **epfiesta.com** or just call/text us at **(915) 268-3997** and we'll send a same-day quote tailored to {{street}}, {{city}}.
>
> Thanks for reading — I'd love to be the team that keeps your next event in the shade.
>
> — Mario
> EP Fiesta — Party Rentals El Paso
> epfiesta.com  •  (915) 268-3997

---

> Hola equipo de {{title}},
>
> Los veranos de West Texas no dan tregua, y tampoco los planes de {{use_case_es}} en {{title}}. Soy Mario de **EP Fiesta**, la empresa de renta de carpas y equipo para eventos de El Paso — les escribo porque los eventos que viene en los próximos meses se disfrutan mucho mejor (y más frescos) con buena sombra para sus invitados.
>
> Entregamos, instalamos profesionalmente y recogemos **carpas high-peak grado comercial**, diseñadas para el viento y el sol de El Paso. Nuestras carpas de 20x20 son modulares: la sombra crece junto con la lista de invitados — desde una 20x20 sobre la mesa de bienvenida hasta una 20x60 cubriendo todo el evento. También rentamos **pop-up canopies** para reuniones más pequeñas, además de **mesas, sillas, luces tipo string** y **liners** (forros decorativos) para dar al espacio un acabado tipo boda.
>
> **Oferta verano 2026 para {{title}}:** reserva tu carpa con al menos **3 meses de anticipación** y te damos **15% de descuento** sobre la renta. La mayoría de los eventos de {{category}} que necesitan carpa caen en el regreso a clases y el otoño — apartar la fecha ahora les asegura el mejor precio y nuestra primera disponibilidad de equipo.
>
> Las rentas empiezan en **$79 USD**. Pueden reservar en **epfiesta.com** o simplemente llamarnos / mandarnos WhatsApp al **(915) 268-3997** y les enviamos una cotización el mismo día, adaptada a {{street}}, {{city}}.
>
> Gracias por leer — me encantaría ser el equipo que mantenga su próximo evento bajo la sombra.
>
> — Mario
> EP Fiesta — Renta de Equipo para Fiestas en El Paso
> epfiesta.com  •  (915) 268-3997

---

## Notes for the operator (you)

- The two paragraphs **`{{use_case_en}}`** and **`{{use_case_es}}`** are pre-written per category in `mailmerge_contacts.csv`. That's where the per-recipient personalization comes from — a Catholic church gets "kermés / first communions / outdoor masses", an elementary school gets "field day / fall carnival / back-to-school night", etc.
- The offer line ("3 months in advance → 15% off") presumes the campaign sends out by mid-July at the latest, which lines up with mid-October events. If you push send beyond August, swap to "book by Sept 30 → 15% off".
- If you want a phone-script version for callbacks from this letter, ping me — same merge fields, much shorter copy.
- Compatible with Google Sheets + YAMM, Mailchimp `*|TITLE|*` syntax (renaming braces), and Word/Docs mail merge. The `{{field}}` braces are the Mustache/Handlebars convention most modern tools use.
