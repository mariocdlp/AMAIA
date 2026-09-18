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
3. Long-presses items for a context menu (duplicate, properties, chairs, tablecloths, tent extras, dance floor size).
4. Sees a running quote (items × prices) at all times.
5. Exports/shares the plan (image + itemized quote) — this is the lead-capture moment.

---

## 2. Design rules (hard constraints)

These are product invariants, not preferences:

1. **True scale, no resizing.** Tables, chairs, and tents render at their real-world footprint against the canvas scale. There are no resize handles by design. Users can only **move** and **rotate** items.
2. **Z-order is fixed by category.** Three layers, bottom to top: **tents**, then **dance floors**, then **tables and chairs**. Placing a table "inside" a tent is purely spatial — the tent never occludes it. Within a layer, later-placed items draw on top, but this never crosses the tent/furniture boundary.
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
| Dance floors | 9×12 · 12×12 · 12×15 · 15×15 · 18×18 · 21×21 ft (3 ft panels) |

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

Quote lines for extras are labeled per size, e.g. **"String Lights (10×20) — $35"**, never a generic "String Lights". Wall and window prices above are for a full set of four sides; partial sets are billed per panel (§4a).

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

### Tent capacity

These fall out of the clearance rules in §5c rather than being typed in by hand, and they agree with standard rental capacity charts.

| Tent | Area | 5 ft rounds | Seats | 8 ft banquet |
|---|---|---|---|---|
| 10×10 | 100 sq ft | 1 | 8 | 1 |
| 10×20 | 200 sq ft | 2 | 16 | 2 |
| 20×20 | 400 sq ft | 4 | 32 | 4 |

Anything beyond these numbers is placed outside the tent rather than squeezed in — see §5c.

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
| — Walls / Windows | Chosen **per side**, not all-or-nothing — see §4a. 10×10 & 10×20 offer "Wall Kit"; 20×20 offers "Side Walls" and "Windows" independently. Visual: only the selected edges are drawn, and they turn with the tent |
| — Ceiling liner | Visual: liner tint on tent canopy. Quote: "price on request" until priced |
| — Leg liners | Visual: accent on the 4/6 corner posts. Quote: "price on request" until priced |
| **Rotate 90°** | Tents rotate in 90° steps only (rectangular footprints) |
| **Delete** | Remove tent (contents stay — furniture is never parented to the tent) |

### 4a. Per-side walls and windows

Walls are almost never wanted on all four sides. A tent gets walled on the windward side, or across the back, or three sides with the view left open — so walls and windows are chosen **per side**, not as a single enclosure toggle.

- **Model.** Each per-side extra stores a set of four sides in the tent's *own* frame (`sides: {walls: {n,e,s,w}, windows: {…}}`), so rotating the tent carries the walls with it.
- **Control.** The tent's context menu shows a picker shaped like the tent itself — a rectangle in the tent's real proportions with a tappable bar on each edge — plus **All 4 sides** and **None** shortcuts. It reads at a glance which sides are closed, and it matches what's drawn on the canvas.
- **Drawing.** Only the selected edges are drawn: walls as a solid edge, windows as a dashed one. A side with both shows the window dashes over the wall.
- **Windows** are independent of walls on the 20×20, since a window panel replaces a wall panel on that side in practice.

**Pricing.** A full set of four is billed at the listed kit price, exactly as the price list reads. A partial set is billed per panel at a quarter of the kit:

| Tent | Extra | All four | Per panel |
|---|---|---|---|
| 10×10 | Wall Kit | $15.00 | $3.75 |
| 10×20 | Wall Kit | $15.00 | $3.75 |
| 20×20 | Side Walls | $25.00 | $6.25 |
| 20×20 | Windows | $35.00 | $8.75 |

The quote line says which it is — "Side Walls (20×20) — all 4 sides $25.00" versus "2 × Side wall panel (20×20) $12.50".

> **Open question:** the quarter-of-a-kit per-panel price is an assumption, not a quoted rate. Confirm how partial wall sets are actually billed — per panel, per side at a flat rate, or kit-only with no partial option — before this ships. The full-set price matches the supplied list exactly either way.

### 4b. Dance floors

A dance floor is a third item category, alongside tents and tables. It sits on its own layer — **above the tent, below tables and chairs** — so it reads as flooring rather than furniture.

**Stocked sizes.** Rental floors are built from 3 ft panels, so every stocked size is a multiple of 3. Chosen from a radio list, never typed:

| Size | Area | Dancers at 3 sq ft | Suits (at 50% dancing) |
|---|---|---|---|
| 9×12 | 108 sq ft | 36 | up to ~72 guests |
| 12×12 | 144 sq ft | 48 | up to ~96 |
| 12×15 | 180 sq ft | 60 | up to ~120 |
| 15×15 | 225 sq ft | 75 | up to ~150 |
| 18×18 | 324 sq ft | 108 | up to ~216 |
| 21×21 | 441 sq ft | 147 | up to ~294 |

**Sizing rule.** The recommendation is the industry one: **half the guests dance at once, each needing 3 sq ft.** So `area = guests × 0.5 × 3`, and the app marks the smallest stocked floor that covers it. The picker shows the arithmetic rather than just the answer — *"50 dancing × 3 sq ft = 150 sq ft — smallest floor that covers it is 12×15"* — and the guest count is pre-filled from the plan's own seat count but editable, so changing it moves the **recommended** badge live.

**Placement.** A dance floor asked for in a prompt goes in the **last tent** — the dancing tent — and when tents are auto-picked the app adds one for it, since a floor of any usable size fills most of a 20×20. Tables are then rung around it (the open-centre pattern) and kept a foot clear. A floor added by hand lands in the nearest clear spot rather than on top of whatever is already placed, and shuffle treats it as a fixed obstacle.

> **Open question:** dance floors are quoted **price on request** — the supplied inventory has no dance floor pricing. The size, area and dancer capacity carry through to the estimate, so only the rate is missing. Typically these are billed per panel or per square foot; send a rate and it becomes a live line.

### Chairs
No context menu of their own in v1 — chairs are managed entirely through their parent table.

---

## 5. Auto layout — prompt box + guided auto-arrange

Two doors to the same layout engine: type a sentence, or answer four questions.

### 5a. Prompt box (primary)

A persistent input sits directly under the canvas: **"Describe your event…"** with a ✨ build button. One sentence produces a complete, to-scale, fully priced plan.

> *"20×20 tent with 5 round tables, white tablecloths and 40 padded chairs."*
> → 1 × 20×20 tent · 5 × 5 ft round · 40 padded white chairs · spandex white — **$520**

**Why it matters:** it collapses the whole planning flow into the sentence a customer would say to a rental rep on the phone. It's the feature that makes the perk feel effortless, and it's the fastest path to a quote.

**What it understands** (deterministic on-device parser — no network call, instant, works offline):

| Input | Recognized |
|---|---|
| Tents | `20×20 tent`, `two 10×20 tents`, `3 tents of 10×10`, `20×20 tent x2`, mixed sizes in one sentence (`a 10×10 tent and a 20×20 tent`), `a tent` / `2 tents` with no size (auto-picks the smallest that fits the tables), off-catalog sizes (mapped to stocked sizes with a note) |
| Tables | `5 round tables`, `8 ft tables`, `six foot tables`, `10 cocktail tables`, bare `6 tables` (defaults to 5 ft round) |
| Chairs | `40 padded chairs`, `basic chairs`, `no chairs`, `seating for 50` |
| Guests | `60 guests`, `for 24 people` — derives table count at standard seating (MIN per table) |
| Linens | `white tablecloths`, `black spandex` |
| Tent extras | `string lights` / `bistro lights`, `walls`, `windows`, `ceiling liner`, `leg liners` |
| Venue | `in a 30×50 yard` — sets the canvas, and the venue auto-grows if the tents need more room |
| Number words | `two`, `six`, `a dozen`, `a hundred` |

**Read-back, not silence.** Every run answers with what it understood plus the price, and flags what the plan can't deliver — *"Seated 32 of 40 — add a table or a bigger tent for the rest"*, *"Tight fit — chairs nearly touch. A bigger tent would breathe better."* The tight-fit warning is an honest upsell: it fires when aisles drop under 3 ft.

**Edit mode.** If the prompt only mentions properties and the canvas already has items — *"add string lights and black tablecloths"* — it edits what's there instead of rebuilding. Chairs, linens, and tent extras apply across every matching item at once.

**Undo.** Every prompt snapshots the layout first; the read-back carries an **Undo** button, so a misread sentence is never destructive.

**Fallback.** Unrecognized input never clears the canvas — it answers with an example prompt instead.

> **v1 implementation note:** the parser is a rule-based, on-device matcher, chosen over an LLM call so results are instant, free, private, and identical every time — which is what a demo and a quote both need. An LLM fallback for genuinely unusual phrasing is a v2 candidate, not a v1 dependency.

### 5b. Guided auto-arrange

For users who'd rather tap than type, an **"Auto ✨"** button on the quote bar opens a 4-step sheet:

1. **How many guests?** — numeric stepper/keypad.
2. **Table type** — 5 ft round / 6 ft banquet / 8 ft banquet (cocktail excluded from seated auto-arrange; offered as an optional "add N cocktail tables" extra).
3. **Tent?** — None / 10×10 / 10×20 / 20×20 / **"Choose for me"** (app picks the smallest tent — or combination — whose capacity covers the guest count).
4. **Chair type** — Basic / Padded white.

It builds the same spec object the prompt parser produces and hands it to the same layout engine — one code path, two front doors.

### 5c. Accommodation guidelines

Generated layouts are held to real event-planning clearances. These are product rules, not tuning constants — **no generated layout may ever place one table's chairs on top of another's.** That is the hard invariant; everything below exists to satisfy it while still packing a space sensibly.

The unit that matters is the **lane**: the clear floor left between whatever occupies the space — a chair back on one side, and a chair back or table edge on the other.

| Clearance | Value | Reasoning |
|---|---|---|
| Chair depth behind a table | 1.72 ft | seat plus pull-back room |
| Lane between chairs — ideal | 1.5 ft | with two chair backs this is the industry-standard 5 ft between round tables |
| Lane between chairs — floor | 0.5 ft | chairs close but never touching; layouts at this lane are flagged "snug" |
| Chair back to tent leg | 0.75 ft | perimeter clearance inside a tent |
| Chair back to canvas edge | 2.5 ft | perimeter clearance with no tent |
| Lane between cocktail tables | 2 ft ideal, 1 ft floor | mingling room, no chairs to clear |

**Clearance is directional.** A banquet table only seats guests on its long sides unless it's set to MAX, so it needs no chair clearance at its ends and packs end to end the way it really does. Round tables need clearance on every side. The engine evaluates both orientations for rectangular tables and takes whichever fits the requested count at the most generous lane.

**Resulting capacities at proper spacing** — these match standard rental capacity charts, which is the check that the constants are right:

| Tent | Area | 5 ft rounds | Seats |
|---|---|---|---|
| 10×10 | 100 sq ft | 1 | 8 |
| 10×20 | 200 sq ft | 2 | 16 |
| 20×20 | 400 sq ft | 4 | 32 |

**When the request exceeds what fits**, the app never shrinks the spacing past the floor. It places what fits inside, puts the remainder outside the tent at proper spacing, and says so with the real number: *"1 table placed outside the tent — it doesn't fit inside with proper aisles. A 20×20 seats about 32 at 5 ft round tables."* On an open canvas with no tent, it grows the canvas instead. This is an honest upsell: the customer sees exactly why they need the bigger tent.

### 5d. Arrangements and shuffle

A **shuffle** button beside the prompt box re-lays the tables inside their tent. Same tables, same chairs, same quote — a different arrangement. It's the "show me another option" move a planner makes in front of a client, and it's what turns the app from a drawing tool into something that gives advice.

**Named arrangements** — each press moves to the next one that fits, and the read-back names it so the customer learns the vocabulary:

| Arrangement | What it is | When it shows |
|---|---|---|
| **Banquet grid** | even rows and columns | always, when anything fits |
| **Staggered rows** | alternate rows offset half a pitch, for sightlines | 2+ rows |
| **Open centre** | seating rings the tent, middle left clear for dancing | enough tables to ring the space |
| **Centre aisle** | two blocks with a 4 ft processional lane between | 4+ tables, room for the lane |
| **Feasting table** | banquet tables joined end to end, family style | rectangular tables at MIN seating |
| **U-shape** | head table with two arms, everyone facing in | 3+ rectangular tables |

**How it decides what to offer.** Every pattern is *generated, then validated* — bounds-checked against the tent interior and collision-checked table by table, including chairs, against each other and against anything staying put. A pattern that can't be laid out cleanly is simply never offered, so shuffle can't produce a bad plan. Patterns whose tables are meant to meet (a feasting run, a U-shape) are validated at zero clearance — touching is fine, overlapping never is, because the collision box already includes each chair's depth.

**Scope.** Shuffle works inside tents. Tables outside a tent stay where they are and become fixed obstacles the new arrangement has to clear, so re-arranging a tent can never throw a table on top of something already placed. With no tent, the whole canvas is the area. Every shuffle is one undo step.

> **Known gap for v1:** chairs currently ring every table, so a U-shape is drawn with chairs on the inside faces too. A true U-shape seats guests only on the outer edge. Doing that properly needs per-side chair control on a table, which is a data-model change — it's a v2 candidate, not a shuffle fix.

### Algorithm (v1 — deterministic grid, good enough beats clever)

```
tables_needed = ceil(guests / seats_per_table)
chairs_per_table decides the clearance pads (ends only seat at MAX)

if tent selected/auto:
    pack the requested tents edge to edge into rows (wrapping at the
    canvas width, rows centered) — sizes may be mixed, so each tent is
    packed by its own footprint; grow the canvas if the pack needs it
    usable_area = each tent's interior less the perimeter clearance
    tables are split evenly across the tents, capped by what each holds
else:
    usable_area = canvas less the open-air perimeter clearance
    grow the canvas rather than tighten the lane below ideal

grid-place tables in usable_area, trying lanes from 3 ft down to the
floor and both orientations for rectangles; take the most generous lane
that still fits the requested count. Partial rows are centered.
lane < ideal → flag "snug" in the read-back (never an overlap)

chairs are distributed round-robin across the tables, capped at each
table's MAX, so 40 across 5 rounds = 8 each and 43 = 9/9/9/8/8

overflow: tables that don't fit inside the tent at proper clearance are
placed outside it, below the tents, with a note naming the tent's real
seated capacity; guests that can't be seated are reported in the read-back
```

- Both doors **replace** the current layout, always behind **Undo** — offered inline in the read-back and always available from the history controls.
- Result is fully editable afterwards — it's a starting point, not a lock-in.
- The view zooms to the generated plan rather than the whole lot, so the layout is legible on a phone without pinching.
- Quote updates instantly, which makes this an **instant estimator**: "50 guests under a tent ≈ $X" in one sentence. This is the perk's biggest wow-moment; make it fast (< 0.5 s).

---

## 6. UX blueprint

```
┌──────────────────────────────┐
│  Event Planner   40×60 ft ✎  ?│  ← venue size chip (tap to change), demo guide
├──────────────────────────────┤
│ ⬚ ⤓                      + − ⤢│  ← select mode / save image · zoom
│                              │
│         CANVAS               │   ← pinch-zoom / pan, grid at 1 ft,
│   (venue at chosen scale)    │     dimension labels on edges
│      [3 selected ⧉ ⟳ ✕ Done] │   ← appears while multi-selecting
├──────────────────────────────┤
│ [ Describe your event…    ✨] │  ← prompt box (§5a)
├──────────────────────────────┤
│  Estimate: $520   [Auto ✨]   │  ← persistent quote bar, tap → itemized sheet
├──────────────────────────────┤
│ [Tables ▾] [Tents ▾] [Misc]  │   ← item tray: thumbnails w/ price tags,
│  ▢6ft $8  ▢8ft $10  ◯5ft $10 │     tap or drag onto canvas to place
└──────────────────────────────┘
```

- **New plan flow:** name → venue dimensions (presets: 20×30, 30×50, 40×60, 50×100, 60×120, or custom) → blank canvas. The venue size is always one tap away from the canvas (the size chip in the header) and can also be set from the prompt box — "in a 30×50 backyard" — and it auto-grows when a layout needs more room than it has.
- **Selection:** tap = select (shows rotate handle + price tag), drag = move with edge snapping (soft snap to 6″ increments and to alignment with nearby items), long-press = context menu.
- **Multi-select:** a select-mode toggle on the canvas turns tap into add-to-selection and drag into a lasso; two-finger drag still pans. On a keyboard, holding **Shift, ⌘ or Ctrl** does the same without entering select mode — drag to lasso an area, click to add or remove one item. With a selection active, a floating action bar offers **Select all · Properties · Duplicate · Rotate · Delete**, and dragging any selected item moves the whole group together. Properties is enabled only when exactly one item is selected, since the context menu edits a single item; long-press still opens it too. Duplicating a group clones every item with all of its properties, so a dressed table row copies in one tap.
- **Reaching an item's properties** — three ways, so it is never a dead end: long-press the item, the ••• button on the single-select pill, or the ••• button in the multi-select bar. Transient banners never capture taps (`pointer-events: none` except on their own Undo button), and the canvas suppresses the iOS touch callout so a long-press is never stolen by the system.
- **Undo / redo:** a full history stack, not a one-step revert. Every mutation — a prompt, an auto-arrange, a property toggle, a move, a rotate, a duplicate, a delete, a canvas resize — commits the pre-change state first, so each is individually reversible and replayable. Buttons sit on the canvas next to the select and save controls, ⌘Z / ⌘⇧Z (and Ctrl+Y) work on a keyboard, and a new action after an undo clears the redo branch, as expected. A drag is one entry, not one per frame. History depth is capped at 60 states; a prompt that parses nothing rolls back without leaving a redo step.
- **Quote sheet:** itemized list grouped Tents → Tent extras → Tables → Chairs → Linens, with quantities, unit prices, and total. CTA button: **"Request this quote"** → prefilled email/WhatsApp/booking-form handoff (this is the perk→lead conversion point).
- **Save as image:** renders a print-quality PNG of the plan — title, venue size, item and seat counts, date, the total, the layout drawn to scale with a 10 ft scale bar, and the itemized estimate as a two-column legend. It's the artifact a customer texts to a partner or forwards to the rental team, so it carries the business's name. Always rendered on the light palette regardless of the viewer's theme, so it prints and forwards cleanly.
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
              tentProps:   { stringLights, ceilingLiner, legLiners,  // tents only
                             sides: [ExtraID: SideSet] }?            // per-side walls
            }
SideSet     { n: Bool, e: Bool, s: Bool, w: Bool }   // in the TENT's own frame,
                                                     // so it rotates with the tent
CatalogItem { id, name, category: .table | .tent | .chair,
              footprint: Size(inches), price: Decimal,
              seating: { min, max }?,                     // tables
              extras: [Extra { id, label, price?, perSide, sideLabel }]?  // tents
            }
Quote       // pure function: (Plan, Catalog) -> [QuoteLine] + total
            // a perSide extra bills as the kit price at 4 sides, else
            // price/4 per selected panel
```

Key invariants encoded in the model, not the UI:
- `layer` is derived from `category` (tents → background) — impossible to violate z-order.
- Footprint comes from the catalog — items have no size field, so resizing can't exist.
- Chairs live inside `tableProps`, positioned procedurally around the parent — they can never orphan.

---

## 8. Build roadmap

| Phase | Scope | Est. |
|---|---|---|
| **P1 — Canvas core** | Venue setup w/ presets, scaled canvas w/ grid, item tray, drag-place/move/rotate/delete, multi-select (lasso + bulk duplicate/rotate/delete/group-move), fixed z-layers, undo/redo history, autosave | 3 wk |
| **P2 — Context menus & props** | Long-press menus per §4: duplicate (carries all properties), chair add/type (procedural snap layout around each table shape), tablecloths, tent extras w/ visuals | 2 wk |
| **P3 — Quote engine & export** | Catalog JSON, live quote bar, itemized sheet w/ size-specific extra labels, "Request this quote" handoff, save-as-image (scale bar + legend + total) | 1.5 wk |
| **P4 — Auto layout** | Prompt-box parser + read-back + edit mode (§5a), guided auto-arrange sheet, named arrangements + shuffle (§5d), tent auto-pick, grid placement algorithm, overflow and tight-fit handling | 2.5–3 wk |
| **P5 — Polish & ship** | Onboarding (3-screen), empty states, haptics, App Store assets, TestFlight beta → release | 1–1.5 wk |

**Total: roughly 9–11 weeks** for a solo iOS dev to a shippable v1. P1–P3 alone is a demoable perk (~6.5 wk); P4 carries both headline features (the prompt box and auto-arrange) and is deliberately isolated so it can ship as a fast-follow update if needed.

### v2 candidates (explicitly out of v1)
Free-standing chair rows (ceremonies), **per-side chair control on a table** (so a U-shape seats only its outer edge), dance floor / DJ booth / bar as placeable "misc" items, guest-name seat assignment, iPad layout, iCloud sync & plan sharing links, in-app booking with date availability, an LLM fallback for prompts the rule-based parser can't read.

---

## 9. Risks & open questions

1. **Ceiling liner & leg liner pricing** — in the menu but unpriced; need numbers or confirm "price on request" is acceptable at launch.
2. **Tablecloth pricing** — spandex white/black currently quoted at $0; confirm whether linens are billed.
3. **Dance floor pricing** — dance floors are in the app (§4b) but the supplied inventory has no rate, so they quote as "price on request". Send a per-panel or per-square-foot rate and every size prices itself.
4. **Partial wall pricing** — walls and windows are now chosen per side (§4a). A full set of four bills at your listed kit price; a partial set currently bills at a quarter of it per panel. Confirm how you actually charge for a two- or three-sided job.
5. **Multi-tent auto-arrange** — v1 handles "choose for me" by combining tents in a row (e.g. 2 × 20×20 for 70 guests); confirm combinations you actually stock/install.
6. **Cocktail tables & chairs** — assumed standing-only (no chair options); confirm.
7. **Quote handoff channel** — email, WhatsApp, or a booking form URL? Determines the "Request this quote" CTA integration.
8. **Android** — iPhone-only per brief; if Android demand appears, the model/quote logic ports but UI is a rewrite → revisit React Native/Flutter *only* if cross-platform becomes a requirement before build starts.
