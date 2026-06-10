#!/usr/bin/env python3
"""
Builds A101-ers-ghl-bridge.json from the editable Code-node JS files in code-nodes/.
Run from /home/user/AMAIA/n8n/:  python3 build-workflow.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
DIFF_JS  = (HERE / "code-nodes" / "diff-and-decide.js").read_text()
BUILD_JS = (HERE / "code-nodes" / "build-webhook-payload.js").read_text()
MARK_JS  = """// === A101: Compute fired_at columns for sheet upsert ===
// Carries forward existing *_fired_at values and stamps the one matching _event_type.
const e = $json;
const now = new Date().toISOString();
const row = e._row || {};
const evt = e._event_type;
return [{
  json: {
    order_id: row.order_id,
    customer_id: row.customer_id,
    status_raw: row.status_raw,
    status_norm: row.status_norm,
    total: row.total,
    ers_created_at: row.ers_created_at,
    ers_updated_at: row.ers_updated_at,
    first_seen_at: row.first_seen_at,
    last_seen_at: now,
    last_status: row.status_norm,
    new_checkout_fired_at:   evt === 'new_checkout'   ? now : (row.new_checkout_fired_at   || ''),
    abandoned_cart_fired_at: evt === 'abandoned_cart' ? now : (row.abandoned_cart_fired_at || ''),
    purchase_fired_at:       evt === 'purchase'       ? now : (row.purchase_fired_at       || ''),
    last_error: '',
    retry_count: 0
  }
}];
"""

ERS_BODY_PARAMS = {
    "parameters": [
        {"name": "key",   "value": "={{ $env.ERS_DEV_KEY }}"},
        {"name": "token", "value": "={{ $env.ERS_API_TOKEN }}"},
    ]
}

def ers_http(name, url, node_id, x, y, extra_params=None):
    body_params = {"parameters": list(ERS_BODY_PARAMS["parameters"])}
    if extra_params:
        body_params["parameters"].extend(extra_params)
    return {
        "parameters": {
            "method": "POST",
            "url": url,
            "sendBody": True,
            "contentType": "form-urlencoded",
            "bodyParameters": body_params,
            "options": {"response": {"response": {"neverError": True, "responseFormat": "autodetect"}}}
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [x, y]
    }

def ghl_http(name, env_var, node_id, x, y):
    return {
        "parameters": {
            "method": "POST",
            "url": f"={{{{ $env.{env_var} }}}}",
            "sendBody": True,
            "contentType": "json",
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json) }}",
            "options": {"response": {"response": {"neverError": True, "responseFormat": "autodetect"}}}
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [x, y]
    }

def sheets_read(name, sheet_name, node_id, x, y):
    return {
        "parameters": {
            "operation": "read",
            "documentId": {"__rl": True, "mode": "id", "value": "={{ $env.A101_SHEET_ID }}"},
            "sheetName": {"__rl": True, "mode": "name", "value": sheet_name},
            "options": {}
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [x, y]
    }

def sheets_upsert(name, sheet_name, match_col, node_id, x, y):
    return {
        "parameters": {
            "operation": "appendOrUpdate",
            "documentId": {"__rl": True, "mode": "id", "value": "={{ $env.A101_SHEET_ID }}"},
            "sheetName": {"__rl": True, "mode": "name", "value": sheet_name},
            "columns": {
                "mappingMode": "autoMapInputData",
                "matchingColumns": [match_col],
                "schema": []
            },
            "options": {}
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [x, y]
    }

def code(name, js, node_id, x, y):
    return {
        "parameters": {"language": "javaScript", "jsCode": js},
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x, y]
    }

def switch_node(name, value_expr, cases, node_id, x, y):
    """cases: list of (output_name, match_value)"""
    rules = []
    for output_name, match in cases:
        rules.append({
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                "conditions": [{
                    "leftValue": value_expr,
                    "rightValue": match,
                    "operator": {"type": "string", "operation": "equals"}
                }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": output_name
        })
    return {
        "parameters": {
            "rules": {"values": rules},
            "options": {"fallbackOutput": "none"}
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3,
        "position": [x, y]
    }

nodes = [
    {
        "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 5}]}},
        "id": "trigger",
        "name": "Every 5 minutes",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [200, 400]
    },
    sheets_read("Read orders_state", "A101_orders_state", "read-state", 450, 250),
    sheets_read("Read A101_meta",    "A101_meta",         "read-meta",  450, 400),
    ers_http("ERS: guest_queue", "https://elpasofiesta.ourers.com/api/read/guest_queue/", "ers-guest", 450, 550),
    code("Diff & Decide", DIFF_JS, "diff", 700, 400),
    switch_node("Switch _action", "={{ $json._action }}",
                [("upsert_only", "upsert_only"),
                 ("fire_event",  "fire_event"),
                 ("meta_update", "meta_update")],
                "switch-action", 950, 400),
    sheets_upsert("Upsert orders_state", "A101_orders_state", "order_id", "upsert-state", 1200, 250),
    sheets_upsert("Upsert A101_meta",    "A101_meta",         "key",      "upsert-meta",  1200, 700),
    ers_http("Enrich: ERS account",
             "=https://elpasofiesta.ourers.com/api/read/account/{{ $json.customer_id }}/",
             "ers-enrich", 1200, 450),
    code("Build Webhook Payload", BUILD_JS, "build-payload", 1450, 450),
    switch_node("Switch _event_type", "={{ $json._event_type }}",
                [("new_checkout",   "new_checkout"),
                 ("abandoned_cart", "abandoned_cart"),
                 ("purchase",       "purchase")],
                "switch-event", 1700, 450),
    ghl_http("GHL: new_checkout",   "GHL_WH_NEW_CHECKOUT",   "ghl-new",       1950, 300),
    ghl_http("GHL: abandoned_cart", "GHL_WH_ABANDONED_CART", "ghl-abandoned", 1950, 450),
    ghl_http("GHL: purchase",       "GHL_WH_PURCHASE",       "ghl-purchase",  1950, 600),
    code("Mark fired_at", MARK_JS, "mark-fired", 2200, 450),
    sheets_upsert("Write fired_at row", "A101_orders_state", "order_id", "write-fired", 2450, 450),
]

connections = {
    "Every 5 minutes": {"main": [[{"node": "Read orders_state", "type": "main", "index": 0}]]},
    "Read orders_state": {"main": [[{"node": "Read A101_meta", "type": "main", "index": 0}]]},
    "Read A101_meta":    {"main": [[{"node": "ERS: guest_queue", "type": "main", "index": 0}]]},
    "ERS: guest_queue":  {"main": [[{"node": "Diff & Decide", "type": "main", "index": 0}]]},
    "Diff & Decide":     {"main": [[{"node": "Switch _action", "type": "main", "index": 0}]]},
    "Switch _action": {"main": [
        [{"node": "Upsert orders_state", "type": "main", "index": 0}],   # upsert_only
        [{"node": "Enrich: ERS account", "type": "main", "index": 0}],   # fire_event
        [{"node": "Upsert A101_meta",    "type": "main", "index": 0}],   # meta_update
    ]},
    "Enrich: ERS account": {"main": [[{"node": "Build Webhook Payload", "type": "main", "index": 0}]]},
    "Build Webhook Payload": {"main": [[{"node": "Switch _event_type", "type": "main", "index": 0}]]},
    "Switch _event_type": {"main": [
        [{"node": "GHL: new_checkout",   "type": "main", "index": 0}],
        [{"node": "GHL: abandoned_cart", "type": "main", "index": 0}],
        [{"node": "GHL: purchase",       "type": "main", "index": 0}],
    ]},
    "GHL: new_checkout":   {"main": [[{"node": "Mark fired_at", "type": "main", "index": 0}]]},
    "GHL: abandoned_cart": {"main": [[{"node": "Mark fired_at", "type": "main", "index": 0}]]},
    "GHL: purchase":       {"main": [[{"node": "Mark fired_at", "type": "main", "index": 0}]]},
    "Mark fired_at":       {"main": [[{"node": "Write fired_at row", "type": "main", "index": 0}]]},
}

workflow = {
    "name": "A101 - ERS to GHL Bridge",
    "nodes": nodes,
    "connections": connections,
    "active": False,
    "settings": {
        "executionOrder": "v1",
        "saveExecutionProgress": False,
        "executionTimeout": 240
    },
    "versionId": "",
    "id": "A101-ers-ghl-bridge",
    "meta": {"templateCredsSetupCompleted": False},
    "tags": []
}

out_path = HERE / "A101-ers-ghl-bridge.json"
out_path.write_text(json.dumps(workflow, indent=2))
print(f"Wrote {out_path} ({len(nodes)} nodes)")
