# Event Floor Plan App

A lightweight "Social Tables"-style event floor planner for iPhone, offered as a **free perk** so customers can lay out their event on real rental inventory and walk away with a layout **and a live price quote**.

## Files

| File | What it is |
|---|---|
| [`PLAN.md`](PLAN.md) | The product and technical plan — design invariants, inventory and pricing, context menus, the prompt box, auto-arrange, architecture, and a phased roadmap. |
| [`prototype.html`](prototype.html) | A working interactive prototype. Single file, no build step, no dependencies, no network calls. |

## Running the prototype

Open `prototype.html` in any browser — double-click it, or serve the folder:

```
python3 -m http.server 8000
# then visit http://localhost:8000/docs/event-floor-plan-app/prototype.html
```

On an iPhone, open it in Safari and use **Share → Add to Home Screen** to launch it full-screen like an app.

It is a demo, not the product: everything lives in memory, so a reload starts a fresh plan. It exists to prove the interactions and to put something in front of customers today, and it doubles as the interaction spec for whoever builds the native version.

## What it demonstrates

- **Prompt box** — "20×20 tent with 5 round tables, white tablecloths and 40 padded chairs" builds the plan and prices it. Property-only prompts ("add string lights and black tablecloths") edit what's already on the canvas.
- **Accommodation guidelines** — generated layouts follow real event-planning clearances and never place one table's chairs on top of another's. When a request doesn't fit, the extra tables go outside the tent with a note naming the tent's real seated capacity, rather than being crammed in.
- **True scale, no resizing** — every item is its real footprint against a 1 ft grid.
- **Fixed z-order** — tents always render behind tables and chairs.
- **Long-press context menus** — duplicate (carries all properties), MIN/MAX chairs, chair type, tablecloths; tent extras priced per tent size.
- **Multi-select** — lasso or tap to select (hold Shift or ⌘ on a keyboard), then bulk duplicate, rotate, delete, or move as a group.
- **Live quote** — every item priced from the catalog, with an itemized sheet and a "Request this quote" handoff.
- **Auto arrange** — the guided four-question version of the prompt box.
- **Save as image** — a to-scale PNG with a scale bar and the itemized estimate, ready to send.

## Pricing

Prices live in the `CAT` and `CHAIRS` objects at the top of the prototype's `<script>`. In the real app this becomes a remote-refreshable `catalog.json` so prices change without an app release.

Two items still need numbers from the owner: **ceiling liners** and **leg liners** show as "price on request", and **tablecloths** are quoted as included. See §9 of the plan for the full list of open questions.
