// === A101: Diff & Decide Events ===
// Reads three inputs (immediate parent = fresh ERS poll, plus two referenced nodes
// = sheet state and meta config) and outputs one item per "action" the workflow must take.
//
// Output item shape:
//   { _action: "upsert_only" | "fire_event" | "meta_update",
//     _event_type?: "new_checkout" | "abandoned_cart" | "purchase",
//     _event_id?:   "<order_id>:<event>",
//     ...row fields matching the A101_orders_state schema }
//
// === TODO post-probe ===
// Run A101-PROBE first. The Normalize section below assumes a likely shape for the
// /api/read/guest_queue/ response. After you see the real shape in PROBES.md, adjust
// the field accessors inside `Normalize fresh poll`.

const ABANDONED_THRESHOLD_MIN = 30;
const now = new Date();
const nowIso = now.toISOString();

// --- Load meta tab into a flat object (sheet has key/value rows) ---
const metaRows = $('Read A101_meta').all();
const meta = {};
for (const r of metaRows) {
  const j = r.json || {};
  if (j.key) meta[j.key] = j.value;
}
const bootstrapDone = !!meta.bootstrap_completed_at;

// --- Index prior state by order_id ---
const stateRows = $('Read orders_state').all();
const stateById = {};
for (const r of stateRows) {
  const j = r.json || {};
  if (j.order_id) stateById[String(j.order_id)] = j;
}

// --- Normalize fresh poll (parent input) ---
function statusNorm(raw) {
  if (!raw) return 'other';
  const s = String(raw).toLowerCase();
  if (['paid', 'confirmed', 'complete', 'completed', 'closed', 'won'].includes(s)) return 'paid';
  if (['pending', 'quote', 'open', 'new', 'waiting', 'cart'].includes(s)) return 'pending';
  return 'other';
}

const fresh = [];
for (const it of $input.all()) {
  const j = it.json || {};
  // ERS endpoints sometimes wrap arrays in named keys. Handle a few shapes defensively.
  const records = Array.isArray(j)
    ? j
    : (j.guest_queue || j.queue || j.orders || j.data || j.results || [j]);
  for (const n of (Array.isArray(records) ? records : [records])) {
    if (!n || (!n.order_id && !n.id)) continue;
    fresh.push({
      order_id: String(n.order_id || n.id),
      customer_id: String(n.customer_id || n.customer || ''),
      status_raw: n.status || n.order_status || n.state || '',
      status_norm: statusNorm(n.status || n.order_status || n.state),
      total: Number(n.total || n.amount || n.grand_total || 0),
      ers_created_at: n.created_at || n.created_datetime || n.created || '',
      ers_updated_at: n.updated_at || n.modified_datetime || n.updated || ''
    });
  }
}

const out = [];

// --- Bootstrap path: silent import, NO webhooks ---
if (!bootstrapDone) {
  let maxCreated = '';
  for (const f of fresh) {
    out.push({
      _action: 'upsert_only',
      _bootstrap: true,
      order_id: f.order_id,
      customer_id: f.customer_id,
      status_raw: f.status_raw,
      status_norm: f.status_norm,
      total: f.total,
      ers_created_at: f.ers_created_at,
      ers_updated_at: f.ers_updated_at,
      first_seen_at: f.ers_created_at || nowIso,
      last_seen_at: nowIso,
      last_status: f.status_norm,
      new_checkout_fired_at: 'BOOTSTRAP',
      abandoned_cart_fired_at: f.status_norm === 'paid' ? 'BOOTSTRAP' : '',
      purchase_fired_at: f.status_norm === 'paid' ? 'BOOTSTRAP' : '',
      last_error: '',
      retry_count: 0
    });
    if (f.ers_created_at > maxCreated) maxCreated = f.ers_created_at;
  }
  out.push({
    _action: 'meta_update',
    key: 'bootstrap_completed_at',
    value: nowIso
  });
  out.push({
    _action: 'meta_update',
    key: 'cutoff_order_created_at',
    value: maxCreated
  });
  out.push({
    _action: 'meta_update',
    key: 'last_tick_at',
    value: nowIso
  });
  return out.map(o => ({ json: o }));
}

// --- Normal path ---
for (const f of fresh) {
  const prior = stateById[f.order_id];
  const events = [];

  if (!prior) {
    events.push('new_checkout');
  } else {
    const firstSeen = new Date(prior.first_seen_at || prior.ers_created_at || nowIso);
    const ageMin = (now - firstSeen) / 60000;
    if (f.status_norm === 'pending' && ageMin > ABANDONED_THRESHOLD_MIN && !prior.abandoned_cart_fired_at) {
      events.push('abandoned_cart');
    }
    if (prior.last_status !== 'paid' && f.status_norm === 'paid' && !prior.purchase_fired_at) {
      events.push('purchase');
    }
  }

  const baseRow = {
    order_id: f.order_id,
    customer_id: f.customer_id,
    status_raw: f.status_raw,
    status_norm: f.status_norm,
    total: f.total,
    ers_created_at: prior ? prior.ers_created_at : f.ers_created_at,
    ers_updated_at: f.ers_updated_at,
    first_seen_at: prior ? prior.first_seen_at : nowIso,
    last_seen_at: nowIso,
    last_status: f.status_norm,
    new_checkout_fired_at: prior ? prior.new_checkout_fired_at : '',
    abandoned_cart_fired_at: prior ? prior.abandoned_cart_fired_at : '',
    purchase_fired_at: prior ? prior.purchase_fired_at : '',
    last_error: prior ? prior.last_error : '',
    retry_count: prior ? Number(prior.retry_count || 0) : 0
  };

  if (events.length === 0) {
    out.push({ _action: 'upsert_only', ...baseRow });
  } else {
    for (const ev of events) {
      out.push({
        _action: 'fire_event',
        _event_type: ev,
        _event_id: `${f.order_id}:${ev}`,
        ...baseRow
      });
    }
  }
}

out.push({ _action: 'meta_update', key: 'last_tick_at', value: nowIso });

return out.map(o => ({ json: o }));
