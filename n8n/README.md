# A101 — ERS to GoHighLevel Webhook Bridge (n8n)

Polls Event Rental Systems (ERS) every 5 minutes and fires outbound HTTPS webhooks
to GoHighLevel for three events:

- `new_checkout` — a customer just started a booking
- `abandoned_cart` — a pending order sat for > 30 min without progress
- `purchase` — an order transitioned to paid/confirmed

Built because ERS gates their pre-built GHL integration behind a $99/mo
affiliate plan. We use the documented public ERS API instead, which is
available to any ERS customer with an API token and a dev key.

> ERS has **no native webhook support** (their own docs flag webhooks as a
> feature request). So this workflow polls. 5-minute interval = 6 polls before
> the abandoned-cart threshold trips. Adjust the schedule trigger if you need
> tighter freshness.

---

## ⚠️ First: rotate the leaked credentials

The ERS API token and dev key originally shared with Claude were pasted in
plaintext chat. **Before this workflow goes live**, contact ERS support and
ask for a fresh `dev_key` and regenerate the API token in
`Admin → General Config → API Info`. The new pair goes into n8n environment
variables (below) and **never into this repo or any chat**.

---

## Files

```
n8n/
├── A101-probe.json              # one-shot workflow to discover ERS response shapes
├── A101-ers-ghl-bridge.json     # the main polling workflow (GENERATED — edit JS not JSON)
├── build-workflow.py            # rebuilds the JSON after editing code-nodes/*.js
├── code-nodes/
│   ├── diff-and-decide.js       # the heart of the logic — state diff + event decisions
│   └── build-webhook-payload.js # shapes the JSON sent to each GHL webhook
├── orders_state_template.csv    # headers for the primary state sheet
├── meta_template.csv            # headers for the bootstrap/cutoff/last-tick sheet
├── errors_template.csv          # headers for the append-only error log sheet
├── .gitignore                   # ignores PROBES.md (PII) and *.local.json
└── README.md                    # this file
```

---

## Prerequisites

1. **Self-hosted n8n** (1.x). On a $5 VPS / Docker / Railway — anywhere you
   can set env vars and OAuth-connect to Google.
2. **Google account** with permission to create a Google Sheet for state.
3. **ERS account** with API token + dev key (call ERS support for the dev key
   if you don't have one; it is not gated behind the $99 plan).
4. **GoHighLevel sub-account** with three Inbound Webhook trigger URLs
   created — one per event. (`Automation → Workflows → New → Trigger:
   Inbound Webhook` → copy the URL. Repeat 3x.)

---

## Setup

### 1. Create the Google Sheet

Create one spreadsheet named `A101 - ERS State` with three tabs:

| Tab | Source | Notes |
|---|---|---|
| `A101_orders_state` | `orders_state_template.csv` | the per-order state table; one row per ERS order |
| `A101_meta` | `meta_template.csv` | key/value config; rows for `bootstrap_completed_at`, `cutoff_order_created_at`, `last_tick_at`, `last_tick_status` |
| `A101_errors` | `errors_template.csv` | append-only error log |

Import each CSV in turn, or just paste the header rows directly. The `A101_meta`
tab must already have the four `key` rows in column A (values blank). Grab the
spreadsheet ID from the URL (`docs.google.com/spreadsheets/d/<ID>/edit`).

### 2. Environment variables in n8n

Set these on your n8n instance (Docker env file, `.env`, Railway vars,
wherever your stack puts secrets):

| Variable | Value |
|---|---|
| `ERS_API_TOKEN` | from `Admin → General Config → API Info` in ERS |
| `ERS_DEV_KEY` | from ERS technical support |
| `A101_SHEET_ID` | the Google Sheet ID from step 1 |
| `GHL_WH_NEW_CHECKOUT` | full inbound webhook URL from the GHL workflow that handles new checkouts |
| `GHL_WH_ABANDONED_CART` | same for abandoned carts |
| `GHL_WH_PURCHASE` | same for purchases |

Restart n8n after setting them.

### 3. Connect Google Sheets credential in n8n

`Credentials → New → Google Sheets OAuth2 API`. Authorize the same Google
account that owns the sheet. Name the credential something obvious like
`A101 Sheets` — both `Read` and `Upsert` nodes in the imported workflow will
pick it up automatically on first save.

### 4. Import the probe workflow

`Workflows → Import from File → A101-probe.json`.

Click **Execute Workflow** once. Inspect the output of each HTTP node:

- **`1) /api/test/`** — must return 2xx. If not, your credentials are wrong;
  rotate and retry before doing anything else.
- **`2) /api/read/order_counts/`** — note the response shape. Confirms the
  endpoint exists and what counts mean.
- **`3) /api/read/guest_queue/`** — **the critical one.** Copy the raw response
  into a local file `PROBES.md` (gitignored, do not commit). Note the exact
  field names for: order ID, customer ID, status, total, created/updated
  timestamps. You'll wire these into the Code node next.
- **`4) /api/read/customers/`** — confirms we can resolve customer ID to
  name/email/phone.

### 5. Adjust the Normalize mapping (post-probe)

Open `code-nodes/diff-and-decide.js`. The `Normalize fresh poll` section
guesses common field names (`order_id`, `customer_id`, `status`, `total`,
`created_at`, `updated_at`). If ERS uses different keys, edit those accessors
to match. Then rebuild the JSON:

```bash
cd n8n
python3 build-workflow.py
```

Also check the `statusNorm()` helper. The two lists of strings (`paid`-equivalents
and `pending`-equivalents) should cover whatever values ERS returns for order
states. Add any missing values from your probe output.

### 6. Import the main workflow

`Workflows → Import from File → A101-ers-ghl-bridge.json`.

After import, open each node briefly and confirm:

- **Read orders_state** + **Read A101_meta** + the two upsert sheet nodes —
  pick the `A101 Sheets` credential. The sheet ID resolves from
  `$env.A101_SHEET_ID`.
- **ERS HTTP nodes** — body params already reference `$env.ERS_DEV_KEY` /
  `$env.ERS_API_TOKEN`. Nothing to fill in.
- **GHL HTTP nodes** — URLs reference `$env.GHL_WH_*`. Nothing to fill in.

Leave the workflow **inactive** for now.

### 7. Bootstrap tick

With the sheet still empty, click **Execute Workflow** manually. Expected:

- Every ERS order returned by `guest_queue` is silently written to
  `A101_orders_state` with `*_fired_at` set to `BOOTSTRAP`.
- `A101_meta` updates: `bootstrap_completed_at = <now>`,
  `cutoff_order_created_at = <max ers_created_at observed>`,
  `last_tick_at = <now>`.
- **No GHL webhooks fire.**

If a webhook fires during bootstrap, stop the workflow, clear the sheet, and
review the `bootstrapDone` check in `diff-and-decide.js`.

### 8. Activate

Toggle the workflow on. It will tick every 5 minutes from now until you turn
it off.

---

## How the logic decides events

Per tick, for each order returned by `/api/read/guest_queue/`:

| Condition | Event fired |
|---|---|
| Order not in sheet (and bootstrap already done) | `new_checkout` |
| Order in sheet, status still `pending`, age > 30 min, `abandoned_cart_fired_at` is empty | `abandoned_cart` |
| Order in sheet, previous `last_status != paid`, current `status_norm == paid`, `purchase_fired_at` is empty | `purchase` |
| Otherwise | none — sheet row just gets `last_seen_at` refreshed |

Idempotency is enforced by the `*_fired_at` columns acting as locks: a
webhook only fires when its column is empty. The payload to GHL includes an
`event_id` of the form `<order_id>:<event>` so GHL workflows can dedupe
defensively.

---

## Verification (do this before pointing at real GHL URLs)

1. Set `GHL_WH_NEW_CHECKOUT`, `GHL_WH_ABANDONED_CART`, `GHL_WH_PURCHASE` to
   three distinct throwaway URLs from <https://webhook.site>.
2. Run bootstrap (step 7). Confirm sheet populates, webhook.site shows **zero**
   hits.
3. From an incognito browser, start a real booking on epfiesta.com — fill cart,
   reach checkout, **stop**. Within 5 min, the next tick should:
   - Append a new row to `A101_orders_state` with `new_checkout_fired_at` set.
   - Fire one POST to the new_checkout webhook URL on webhook.site with the
     enriched customer payload.
4. Wait 30+ min without completing the checkout. Next tick after the threshold
   fires `abandoned_cart` exactly once.
5. Let two more ticks pass. **No additional hits** — idempotency confirmed.
6. Complete the booking (mark it paid via ERS admin or pay through the flow).
   Next tick: `purchase` fires once, `purchase_fired_at` populated,
   `last_status` → `paid`.
7. Negative test: point one `GHL_WH_*` env var at `https://webhook.site/404`.
   The workflow's `Mark fired_at` step still runs (we write fired_at BEFORE the
   webhook fires — see "trade-off" in Failure Modes below), so the next tick
   won't retry. To get retry-on-failure, swap to the alternative ordering
   described below.

Once verification passes, swap the env vars to the real GHL Inbound Webhook
URLs and re-activate.

---

## Failure modes & trade-offs

- **ERS API down**: the `ERS: guest_queue` node returns non-2xx with
  `neverError: true`, the Code node sees empty/no items, no events fire, no
  sheet damage. Next tick retries naturally.
- **GHL webhook returns non-2xx**: the workflow currently treats fire-and-mark
  as a single step (we mark `*_fired_at` immediately after the GHL HTTP call
  regardless of response). This avoids the duplicate-webhook problem where a
  timeout-but-delivered request would be re-fired on the next tick.
  **Trade-off**: a real GHL outage means the event is lost. To switch to
  retry-on-failure, change the connection in the workflow so `Mark fired_at`
  only runs when an `IF` node confirms the GHL HTTP returned 2xx. (Easier in
  the n8n UI than in JSON — add an IF node after each GHL HTTP, branch
  success → Mark fired_at, branch failure → Sheets append to `A101_errors`.)
- **Sheet write fails after webhook fires**: extremely unlikely; if it happens,
  the same event will fire again on the next tick because `*_fired_at` is
  still empty. GHL workflows should dedupe on `event_id` as a backstop.
- **Two concurrent ticks**: n8n's Schedule Trigger doesn't overlap by default.
  We also set `executionTimeout: 240` (4 min) so a stuck tick can't collide
  with the next.
- **Cold restart of n8n**: state lives in Google Sheets, not in n8n, so
  restarting the n8n instance doesn't lose progress.

---

## What this workflow does NOT do

- It does not import historical orders into GHL beyond marking them
  `BOOTSTRAP` in the state sheet. To backfill GHL contacts, write a separate
  one-shot workflow that reads `A101_orders_state` and POSTs to a fourth GHL
  webhook URL.
- It does not push order line items, addresses, or payment methods to GHL —
  only customer identity + status + total + timestamps. Extend the
  `build-webhook-payload.js` Code node if you need richer payloads.
- It does not handle ERS cancellations or refunds. Add an extra branch in
  `diff-and-decide.js` if you want a `cancelled` event.
- It does not call `/api/read/order/{order_id}/` for per-order details. If
  `guest_queue` returns enough fields, this isn't needed; if not, add a
  per-event enrichment call before `Build Webhook Payload`.

---

## Editing & rebuilding

The workflow JSON is generated from `build-workflow.py` plus the JS files
in `code-nodes/`. To change logic:

1. Edit `code-nodes/diff-and-decide.js` or `code-nodes/build-webhook-payload.js`.
2. Run `python3 build-workflow.py` to regenerate `A101-ers-ghl-bridge.json`.
3. Re-import into n8n (or copy/paste the Code node body via n8n's UI for a
   live tweak without re-importing).

To change node graph shape (add/remove nodes, change connections), edit
`build-workflow.py` directly and rebuild.

---

## Naming convention

Workflow ID `A101` per AMAIA convention (`A` + 3 digits — see
`/.claude/skills/propuesta/plan-base.md`). The `A1xx` band is used for n8n
bridges and external integrations, distinct from `A001-A099` which is
reserved for native GHL workflows.
