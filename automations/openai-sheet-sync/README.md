# openai-sheet-sync

Weekly automation that pushes the latest tab of a Google Sheet into the File
Search store attached to an OpenAI prompt.

## Flow

1. **Trigger** — every Tuesday at 06:00 in the script's timezone.
2. **Read** — opens the spreadsheet, takes the **leftmost** sheet tab
   (convention: newest tab on the left), reads the data range with the first
   row as headers.
3. **Convert** — each data row becomes a JSON object keyed by header. The
   output is a single JSON array.
4. **Replace file** — lists the files attached to the prompt's vector store,
   detaches them and deletes them from Files storage, then uploads the new
   JSON and attaches it to the same vector store. The prompt keeps pointing
   at the same `vs_…` ID, so the new content is live immediately.
5. **(Optional) Promote version** — if `PROMOTE_VERSION=true`, the script
   creates a new prompt version mirroring the current config and sets it as
   the default. Use this only if you want an audit trail of weekly updates;
   the vector store content is already replaced regardless.

## Required Script Properties

Set these in Apps Script → Project Settings → Script properties. They are
encrypted at rest and never appear in the script source.

| Key | Value |
| --- | --- |
| `OPENAI_API_KEY` | Dedicated key (see "API key handling" below) |
| `SPREADSHEET_ID` | `125Dff05vUD_bzUPeGwZfbqoCI-BGJN-VFd9CFCg5Qns` |
| `PROMPT_ID` | `pmpt_69c6b252ac148194b70df4cd1baceeb80b80aa2f6e225388` |
| `VECTOR_STORE_ID` | `vs_…` — copy once from the prompt's File Search panel |
| `PROMOTE_VERSION` | `true` to bump the prompt's default version each run (optional) |

## One-time setup

1. Open the target Google Sheet, then Extensions → Apps Script.
2. Paste `Code.gs` into the editor, save.
3. Add the Script Properties above.
4. Run `installTrigger()` once. Accept the OAuth consent for Sheets +
   external request scopes — this happens under your own Google account, so
   no service account or Google API key is needed.
5. Run `syncSheetToOpenAI()` manually once and verify in the OpenAI
   dashboard that the prompt's File Search has the new JSON attached.

## API key handling

**Never paste API keys in chat (including to me) or commit them anywhere in
this repo.** They belong in Script Properties only.

Recommended setup:

- Create a **new** OpenAI API key dedicated to this automation. Name it
  `amaia-sheet-sync` so it's obvious in the dashboard. Restrict it to a
  project that only has access to the relevant prompt and vector store.
- Set a monthly usage cap on that key in OpenAI → Settings → Limits, so a
  bug can't run up charges.
- Paste the key directly into Apps Script Project Properties. If someone
  else needs to set it, share via 1Password / Bitwarden item with an
  expiring share link — not Slack, email, or chat.
- Rotate the key quarterly: create a new one, update the Script Property,
  delete the old one in the OpenAI dashboard.
- For Google: nothing to share. The script runs as the Google user that
  authorized `installTrigger()`, using built-in OAuth.

## Verifying / debugging

- View → Executions in Apps Script shows each run, its log output, and
  errors with stack traces.
- The script logs sheet name, row count, file ID, and vector store ID on
  success. If a run fails, the trigger keeps firing weekly — fix the cause
  and re-run `syncSheetToOpenAI()` manually to catch up.
- If the prompt's `vector_store_id` ever changes (e.g. someone edits the
  prompt manually), update the `VECTOR_STORE_ID` Script Property.

## Notes / assumptions

- "Newest tab is leftmost" is a convention you maintain manually. The
  script always picks index 0. Verify the sheet name in the execution log
  after the first run.
- Row 1 is treated as headers. Empty rows are skipped.
- The OpenAI Prompts versioning endpoints (`POST /v1/prompts/{id}/versions`,
  `default_version_id`) are documented under the Prompts API. If they
  change shape, the vector-store replacement still works on its own — leave
  `PROMOTE_VERSION` unset.
