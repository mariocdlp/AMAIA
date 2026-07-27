# Event Floor Plan App — Product & Technical Plan (iPhone)

A lightweight "Social Tables"-style floor planner for iPhone, offered as a **free perk** so customers can lay out their event space using the real rental inventory (tables, chairs, tents) — and walk away with a layout **and a live price quote** that maps 1:1 to what they'd rent.

---

## 1. Product summary

| | |
|---|---|
| **Platform** | iPhone (iOS 17+), portrait + landscape |
| **Positioning** | The simplest possible event layout tool — no accounts required to start, no CAD complexity |
| **Business goal** | Perk that funnels users toward a rental quote: every item placed has a real price, and the plan totals into an instant estimate |
| **Non-goals (v1)** | Seating charts / guest name assignment, 3D view, multi-room venues, collaboration, custom furniture, item resizing |

### Core loop
1. User sets their space (lot/venue dimensions, e.g. 40 ft × 60 ft backyard).
2. Drags inventory items from a tray onto a scaled canvas.
3. Long-presses items for a context menu (duplicate, properties, chairs, tablecloths, tent extras).
4. Sees a running quote (items × prices) at all times.
5. Exports/shares the plan (image + itemized quote) — this is the lead-capture moment.

---

## 2. Design rules (hard constraints)

These are product invariants, not preferences:

1. **True scale, no resizing.** Tables, chairs, and tents render at their real-world footprint against the canvas scale. There are no resize handles by design. Users can only **move** and **rotate** items.
2. **Z-order is fixed by category.** Tents always render on the background layer; tables and chairs always render on the foreground layer. Placing a table "inside" a tent is purely spatial — the tent never occludes it. Within a layer, later-placed items draw on top, but this never crosses the tent/furniture boundary.
3. **"Right click" = long-press context menu.** iPhone has no right click; the equivalent interaction is a long-press that opens a native context menu (`UIContextMenuInteraction` / SwiftUI `.contextMenu`). Menu contents are per-item-type (§4).
4. **Chairs belong to tables.** Chairs are not free-floating v1 objects — they attach to a parent table via the table's context menu, auto-snap around it, and move/rotate with it. (Free-floating chair rows, e.g. ceremony seating, is a v2 candidate.)

### Real-world footprints (used for scale rendering and auto-arrange)

| Item | Footprint |
|---|---|
| Basic / padded chair | 17″ × 17″ (~1.5 ft square) |
| 6 ft banquet table | 72″ × 30″ |
| 8 ft banquet table | 96″ × 30″ |
| 5 ft round table | 60″ diameter |
| Cocktail table | 30″ diameter (high-boy) |
| 10×10 tent | 10 ft × 10 ft |
| 10×20 tent | 10 ft × 20 ft |
| 20×20 tent | 20 ft × 20 ft |

---

## 3. Inventory & pricing (single source of truth)

Bundled as a versioned JSON catalog (`catalog.json`) so prices can be updated without an app release (fetch remote, fall back to bundled copy).

### Items

| Item | Price | Item | Price |
|---|---|---|---|
| Basic chair | $1.80 | Cocktail table | $12.00 |
| Padded chair | $3.00 | 10×10 tent | $75.00 |
| 6 ft table | $8.00 | 10×20 tent | $150.00 |
| 8 ft table | $10.00 | 20×20 tent | $350.00 |
| 5 ft round | $10.00 | | |

### Size-specific tent extras (quote label carries the tent size)

| Tent | Extras |
|---|---|
| 10×10 | String Lights $25 · Wall Kit $15 |
| 10×20 | String Lights $35 · Wall Kit $15 |
| 20×20 | String Lights $55 · Side Walls $25 · Windows $35 |

Quote lines for extras are labeled per size, e.g. **"String Lights (10×20) — $35"**, never a generic "String Lights".

> **Open pricing items (need owner input before v1 ships):**
> - **Ceiling liners** and **leg liners** appear in the tent properties menu but have no price in the extras table → shown in the menu, added to the quote as **"price on request"** until priced.
> - **Tablecloths** (spandex white / spandex black) have no listed price → treated as **$0 / included** in the quote until priced.
> - Padded chair is listed as "padded **white** chair" in the chair-type toggle — catalog name: *Padded white chair*, $3.00.

### Seating capacity per table (drives min/max chairs and auto-arrange)

| Table | MIN chairs | MAX chairs |
|---|---|---|
| 6 ft banquet | 6 (3 per long side) | 8 (+1 per end) |
| 8 ft banquet | 8 (4 per long side) | 10 (+1 per end) |
| 5 ft round | 8 | 10 |
| Cocktail | 0 (standing) | 0 — chair options disabled/hidden |

### Tent capacity (auto-arrange planning numbers, ~10–12 sq ft per seated guest)

| Tent | Area | Seated capacity (rounds) | Fits |
|---|---|---|---|
| 10×10 | 100 sq ft | ~8–10 | 1 × 5 ft round **or** 2 × 6 ft banquet |
| 10×20 | 200 sq ft | ~16–20 | 2 × 5 ft round **or** 4 × 6 ft banquet |
| 20×20 | 400 sq ft | ~32–40 | 4 × 5 ft round **or** 8 × 6 ft / 6 × 8 ft banquet |

---

## 4. Context menus (long-press)

### Tables

| Action | Behavior |
|---|---|
| **Duplicate** | Clone the table **with all its properties** — chair count, chair type, and tablecloth — offset placement next to original |
| **Properties ▸** | Submenu: |
| — Add MIN chairs | Snap the table's MIN chair count around it (replaces current chairs) |
| — Add MAX chairs | Snap the table's MAX chair count around it (replaces current chairs) |
| — Chair type ▸ | Toggle: **No chairs · Basic chairs · Padded white chairs** (swaps in place, keeps count; "No chairs" removes them) |
| — Tablecloth ▸ | Toggle: **None · Spandex white · Spandex black** (visual skin change on the table sprite) |
| **Rotate 45°** | Convenience rotation step (also available via two-finger rotate gesture) |
| **Delete** | Remove table + attached chairs |

*Cocktail tables:* chair actions hidden; tablecloth toggle available (spandex is the classic cocktail-table look).

### Tents

| Action | Behavior |
|---|---|
| **Duplicate** | Clone the tent **with all its properties** — every selected extra carries over |
| **Properties ▸** | Checkable toggles (each adds/removes a size-specific quote line): |
| — Bistro/String Lights | Visual: string-light overlay inside tent footprint. Quote: String Lights at the tent's size price |
| — Walls / Windows | 10×10 & 10×20 → single "Wall Kit" toggle. 20×20 → two independent toggles: "Side Walls" and "Windows". Visual: wall outline on tent perimeter |
| — Ceiling liner | Visual: liner tint on tent canopy. Quote: "price on request" until priced |
| — Leg liners | Visual: accent on the 4/6 corner posts. Quote: "price on request" until priced |
| **Rotate 90°** | Tents rotate in 90° steps only (rectangular footprints) |
| **Delete** | Remove tent (contents stay — furniture is never parented to the tent) |

### Chairs
No context menu of their own in v1 — chairs are managed entirely through their parent table.

---

## 5. Auto-arrange (the "NEXT" feature)

A toolbar button **"Auto arrange ✨"** opens a 4-step sheet:

1. **How many guests?** — numeric stepper/keypad.
2. **Table type** — 5 ft round / 6 ft banquet / 8 ft banquet (cocktail excluded from seated auto-arrange; offered as an optional "add N cocktail tables" extra).
3. **Tent?** — None / 10×10 / 10×20 / 20×20 / **"Choose for me"** (app picks the smallest tent — or combination — whose capacity covers the guest count).
4. **Chair type** — Basic / Padded white.

### Algorithm (v1 — deterministic grid, good enough beats clever)

```
tables_needed = ceil(guests / MAX_capacity(table_type))
if tent selected/auto:
    place tent(s) centered in the venue (row of tents if multiple)
    usable_area = tent interior with 2.5 ft perimeter aisle inset
else:
    usable_area = venue canvas with 2.5 ft edge inset

grid-place tables in usable_area:
    rounds   → square grid, ≥ 5 ft table-edge-to-table-edge gap
               (2 chairs back-to-back + walk space)
    banquets → parallel rows, ≥ 4.5 ft between rows
each table gets chairs = min(MAX, remaining_guests), chair type as chosen

overflow: if tables don't fit the tent/venue → banner
    "Fits X of Y guests — try a bigger tent or venue"
    with one-tap "Upgrade tent" action
```

- Auto-arrange **replaces** the current layout after a confirmation ("This clears your current plan — continue?"), with undo available.
- Result is fully editable afterwards — it's a starting point, not a lock-in.
- Quote updates instantly to the generated layout, which doubles as an **instant estimator**: "50 guests under a tent ≈ $X" in four taps. This is the perk's biggest wow-moment; make it fast (< 0.5 s).

---

## 6. UX blueprint

```
┌──────────────────────────────┐
│  My Backyard Party      ⋯    │   ← plan name, overflow (rename/venue size/export)
├──────────────────────────────┤
│                              │
│         CANVAS               │   ← pinch-zoom / pan, grid at 1 ft,
│   (venue at chosen scale)    │     dimension labels on edges
│                              │
├──────────────────────────────┤
│  Quote: $486   [Auto ✨]     │   ← persistent quote bar, tap → itemized sheet
├──────────────────────────────┤
│ [Tables ▾] [Tents ▾] [Misc]  │   ← item tray: thumbnails w/ price tags,
│  ▢6ft $8  ▢8ft $10  ◯5ft $10 │     drag onto canvas to place
└──────────────────────────────┘
```

- **New plan flow:** name → venue dimensions (presets: 20×30, 40×60, 50×100, custom) → blank canvas.
- **Selection:** tap = select (shows rotate handle + price tag), drag = move with edge snapping (soft snap to 6″ increments and to alignment with nearby items), long-press = context menu.
- **Quote sheet:** itemized list grouped Tents → Tent extras → Tables → Chairs → Linens, with quantities, unit prices, and total. CTA button: **"Request this quote"** → prefilled email/WhatsApp/booking-form handoff (this is the perk→lead conversion point).
- **Export:** share sheet with (a) rendered plan image (PNG, with scale bar + item legend) and (b) itemized quote (PDF or text). Watermarked with the business name/logo.
- **Persistence:** plans autosave locally; multiple plans on a home screen ("My events").

---

## 7. Technical architecture

| Layer | Choice | Why |
|---|---|---|
| Language/UI | **Swift + SwiftUI** | Native context menus, share sheet, gestures for free |
| Canvas | **SpriteKit** scene embedded in SwiftUI (`SpriteView`) | Cheap 2D sprites, z-layers, rotation, hit-testing; overkill-free vs. Metal, more capable than pure SwiftUI Canvas for drag interactions with dozens of nodes |
| State | Observable model (`@Observable`), unidirectional | Plan = value-type document → trivial undo/redo via snapshots |
| Persistence | Codable JSON documents on disk (+ iCloud sync v2) | No server needed for v1 |
| Catalog | Bundled `catalog.json`, remote-refreshable | Price updates without app release |
| Export | `ImageRenderer` / SpriteKit texture render → PNG; PDFKit for quote | Native |
| Distribution | App Store (free) | Perk = zero friction; TestFlight for beta |

### Data model (core entities)

```swift
Plan        { id, name, venueSize: Size(ft), items: [PlacedItem], createdAt }
PlacedItem  { id, catalogID, position: Point(ft), rotation: Degrees,
              layer: .background | .foreground,          // derived from category
              tableProps:  { chairCount, chairType, tablecloth }?,   // tables only
              tentProps:   { stringLights, wallKit, sideWalls,
                             windows, ceilingLiner, legLiners }?      // tents only
            }
CatalogItem { id, name, category: .table | .tent | .chair,
              footprint: Size(inches), price: Decimal,
              seating: { min, max }?,                     // tables
              extras: [Extra { id, label, price?, sizeLabel }]?       // tents
            }
Quote       // pure function: (Plan, Catalog) -> [QuoteLine] + total
```

Key invariants encoded in the model, not the UI:
- `layer` is derived from `category` (tents → background) — impossible to violate z-order.
- Footprint comes from the catalog — items have no size field, so resizing can't exist.
- Chairs live inside `tableProps`, positioned procedurally around the parent — they can never orphan.

---

## 8. Build roadmap

| Phase | Scope | Est. |
|---|---|---|
| **P1 — Canvas core** | Venue setup, scaled canvas w/ grid, item tray, drag-place/move/rotate/delete, fixed z-layers, autosave | 2–3 wk |
| **P2 — Context menus & props** | Long-press menus per §4: duplicate (carries all properties), chair add/type (procedural snap layout around each table shape), tablecloths, tent extras w/ visuals | 2 wk |
| **P3 — Quote engine** | Catalog JSON, live quote bar, itemized sheet w/ size-specific extra labels, "Request this quote" handoff, PNG/PDF export | 1–1.5 wk |
| **P4 — Auto-arrange** | 4-question sheet, tent auto-pick, grid placement algorithm, overflow handling | 1.5–2 wk |
| **P5 — Polish & ship** | Onboarding (3-screen), empty states, haptics, App Store assets, TestFlight beta → release | 1–1.5 wk |

**Total: roughly 8–10 weeks** for a solo iOS dev to a shippable v1. P1–P3 alone is a demoable perk (~5–6 wk); P4 (auto-arrange) is the headline feature but is deliberately isolated so it can ship as a fast-follow update if needed.

### v2 candidates (explicitly out of v1)
Free-standing chair rows (ceremonies), dance floor / DJ booth / bar as placeable "misc" items, guest-name seat assignment, iPad layout, iCloud sync & plan sharing links, in-app booking with date availability.

---

## 9. Risks & open questions

1. **Ceiling liner & leg liner pricing** — in the menu but unpriced; need numbers or confirm "price on request" is acceptable at launch.
2. **Tablecloth pricing** — spandex white/black currently quoted at $0; confirm whether linens are billed.
3. **Multi-tent auto-arrange** — v1 handles "choose for me" by combining tents in a row (e.g. 2 × 20×20 for 70 guests); confirm combinations you actually stock/install.
4. **Cocktail tables & chairs** — assumed standing-only (no chair options); confirm.
5. **Quote handoff channel** — email, WhatsApp, or a booking form URL? Determines the "Request this quote" CTA integration.
6. **Android** — iPhone-only per brief; if Android demand appears, the model/quote logic ports but UI is a rewrite → revisit React Native/Flutter *only* if cross-platform becomes a requirement before build starts.
