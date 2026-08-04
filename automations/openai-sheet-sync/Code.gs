/**
 * AMAIA — Weekly Sheet → OpenAI Vector Store sync.
 *
 * Reads the leftmost (newest) tab of a Google Sheet, converts it to JSON,
 * replaces the file attached to an OpenAI prompt's File Search tool, and
 * optionally promotes a new prompt version as the default.
 *
 * Setup:
 *   1. Open the target spreadsheet → Extensions → Apps Script.
 *   2. Paste this file into Code.gs.
 *   3. Project Settings → Script properties, add:
 *        OPENAI_API_KEY     sk-...
 *        SPREADSHEET_ID     125Dff05vUD_bzUPeGwZfbqoCI-BGJN-VFd9CFCg5Qns
 *        PROMPT_ID          pmpt_69c6b252ac148194b70df4cd1baceeb80b80aa2f6e225388
 *        VECTOR_STORE_ID    vs_... (copy once from the prompt's File Search panel)
 *        PROMOTE_VERSION    "true" to also create + default a new prompt version
 *   4. Run installTrigger() once and accept the OAuth prompt.
 *   5. Run syncSheetToOpenAI() manually once to verify end-to-end.
 */

const OPENAI_BASE = 'https://api.openai.com';

function installTrigger() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'syncSheetToOpenAI')
    .forEach(t => ScriptApp.deleteTrigger(t));

  [ScriptApp.WeekDay.TUESDAY, ScriptApp.WeekDay.FRIDAY].forEach(day => {
    ScriptApp.newTrigger('syncSheetToOpenAI')
      .timeBased()
      .onWeekDay(day)
      .atHour(6)
      .inTimezone(Session.getScriptTimeZone())
      .create();
  });
}

function syncSheetToOpenAI() {
  const cfg = requireConfig([
    'OPENAI_API_KEY',
    'SPREADSHEET_ID',
    'PROMPT_ID',
    'VECTOR_STORE_ID',
  ]);
  const promoteVersion = PropertiesService.getScriptProperties()
    .getProperty('PROMOTE_VERSION') === 'true';

  const { sheetName, json, rowCount } = extractLeftmostSheetAsJson(cfg.SPREADSHEET_ID);
  const filename = `${slug(sheetName)}_${new Date().toISOString().slice(0, 10)}.json`;

  purgeVectorStore(cfg.VECTOR_STORE_ID, cfg.OPENAI_API_KEY);

  const fileId = uploadJsonFile(filename, json, cfg.OPENAI_API_KEY);
  attachFileToVectorStore(cfg.VECTOR_STORE_ID, fileId, cfg.OPENAI_API_KEY);

  if (promoteVersion) {
    promoteNewPromptVersion(cfg.PROMPT_ID, cfg.OPENAI_API_KEY);
  }

  console.log(`OK — sheet "${sheetName}" (${rowCount} rows) → file ${fileId} → vs ${cfg.VECTOR_STORE_ID}`);
}

function extractLeftmostSheetAsJson(spreadsheetId) {
  const sheet = SpreadsheetApp.openById(spreadsheetId).getSheets()[0];
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    throw new Error(`Sheet "${sheet.getName()}" has no data rows`);
  }
  const headers = values[0].map(h => String(h).trim());
  const rows = values.slice(1)
    .filter(row => row.some(cell => cell !== '' && cell !== null))
    .map(row => Object.fromEntries(headers.map((h, i) => [h, row[i]])));
  return { sheetName: sheet.getName(), json: JSON.stringify(rows, null, 2), rowCount: rows.length };
}

function purgeVectorStore(vectorStoreId, apiKey) {
  const list = openai('GET', `/v1/vector_stores/${vectorStoreId}/files?limit=100`, null, apiKey);
  (list.data || []).forEach(f => {
    openai('DELETE', `/v1/vector_stores/${vectorStoreId}/files/${f.id}`, null, apiKey);
    try {
      openai('DELETE', `/v1/files/${f.id}`, null, apiKey);
    } catch (e) {
      console.warn(`Could not delete file ${f.id} from storage: ${e.message}`);
    }
  });
}

function uploadJsonFile(filename, content, apiKey) {
  const boundary = '----amaia' + Utilities.getUuid();
  const head =
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="purpose"\r\n\r\nassistants\r\n` +
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="file"; filename="${filename}"\r\n` +
    `Content-Type: application/json\r\n\r\n`;
  const tail = `\r\n--${boundary}--\r\n`;
  const payload = []
    .concat(Utilities.newBlob(head).getBytes())
    .concat(Utilities.newBlob(content).getBytes())
    .concat(Utilities.newBlob(tail).getBytes());

  const res = UrlFetchApp.fetch(`${OPENAI_BASE}/v1/files`, {
    method: 'post',
    contentType: `multipart/form-data; boundary=${boundary}`,
    headers: { Authorization: `Bearer ${apiKey}` },
    payload: payload,
    muteHttpExceptions: true,
  });
  return parseOpenAIResponse(res, 'POST /v1/files').id;
}

function attachFileToVectorStore(vectorStoreId, fileId, apiKey) {
  const attached = openai('POST', `/v1/vector_stores/${vectorStoreId}/files`, { file_id: fileId }, apiKey);
  const deadline = Date.now() + 5 * 60 * 1000;
  let status = attached.status;
  while (status === 'in_progress' && Date.now() < deadline) {
    Utilities.sleep(3000);
    status = openai('GET', `/v1/vector_stores/${vectorStoreId}/files/${fileId}`, null, apiKey).status;
  }
  if (status !== 'completed') {
    throw new Error(`Vector store ingestion did not complete (status=${status})`);
  }
}

function promoteNewPromptVersion(promptId, apiKey) {
  const prompt = openai('GET', `/v1/prompts/${promptId}`, null, apiKey);
  const version = openai('POST', `/v1/prompts/${promptId}/versions`, {
    tools: prompt.tools,
    messages: prompt.messages,
    model: prompt.model,
  }, apiKey);
  openai('POST', `/v1/prompts/${promptId}`, { default_version_id: version.id }, apiKey);
}

function openai(method, path, body, apiKey) {
  const res = UrlFetchApp.fetch(`${OPENAI_BASE}${path}`, {
    method,
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${apiKey}` },
    payload: body ? JSON.stringify(body) : null,
    muteHttpExceptions: true,
  });
  return parseOpenAIResponse(res, `${method} ${path}`);
}

function parseOpenAIResponse(res, label) {
  const code = res.getResponseCode();
  const text = res.getContentText();
  if (code >= 400) throw new Error(`OpenAI ${label} → ${code}: ${text}`);
  return text ? JSON.parse(text) : {};
}

function requireConfig(keys) {
  const props = PropertiesService.getScriptProperties();
  const cfg = {};
  const missing = [];
  keys.forEach(k => {
    const v = props.getProperty(k);
    if (!v) missing.push(k);
    cfg[k] = v;
  });
  if (missing.length) throw new Error(`Missing Script Properties: ${missing.join(', ')}`);
  return cfg;
}

function slug(s) {
  return String(s).replace(/[^a-zA-Z0-9-_]+/g, '_').replace(/^_+|_+$/g, '') || 'sheet';
}
