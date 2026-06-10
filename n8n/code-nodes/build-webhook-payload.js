// === A101: Build Webhook Payload ===
// Combines the diff item (carries _event_type and order fields) with the customer
// enrichment from the prior HTTP node ($('Enrich: ERS account')) and produces the
// JSON body that goes to the matching GHL Inbound Webhook.

const e = $input.first().json;

// Enrichment from the immediately preceding "Enrich: ERS account" HTTP node.
// Newer n8n versions expose the response under .data or .body depending on options.
const enrichRaw = $('Enrich: ERS account').first().json || {};
const cust = enrichRaw.customer || enrichRaw.data || enrichRaw;

const customer = {
  id: e.customer_id,
  first_name: cust.firstname || cust.first_name || '',
  last_name:  cust.lastname  || cust.last_name  || '',
  email:      cust.email     || '',
  phone:      cust.phone     || cust.mobile_phone || cust.work_phone || '',
  billing_address: cust.billing_address || '',
  billing_city:    cust.billing_city    || '',
  billing_state:   cust.billing_state   || '',
  billing_zip:     cust.billing_zip     || ''
};

return [{
  json: {
    event: e._event_type,
    event_id: e._event_id,
    order_id: e.order_id,
    status: e.status_norm,
    status_raw: e.status_raw,
    total: e.total,
    customer,
    ers_created_at: e.ers_created_at,
    ers_updated_at: e.ers_updated_at,
    source: 'A101-ers-ghl-bridge',
    sent_at: new Date().toISOString(),
    // pass through for downstream sheet-marking node
    _event_type: e._event_type,
    _event_id: e._event_id,
    _row: e
  }
}];
