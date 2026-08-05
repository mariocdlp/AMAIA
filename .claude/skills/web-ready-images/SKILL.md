---
name: web-ready-images
description: Optimize every image in a Google Drive folder for web use — 1:1 centre crop, 1000x1000, 72 DPI, JPEG under 1MB — and deliver them back into a "web optimized" subfolder of the source folder. Invoke when the user says "/web-ready-images", "optimize the images in <Drive folder link>", "make these web ready", "comprime las imágenes de esta carpeta", or pastes a Drive folder link and asks for optimized/compressed/web images.
---

# Skill: Web Ready Images

Take a Google Drive folder, produce web-ready versions of every image in it, and put them where the user asked: a subfolder named **`web optimized`** inside the source folder.

**The input is always a Google Drive folder link.** If the user describes a folder by name or screenshot instead of pasting a link, resolve it to a folder ID first (see Step 1) — do not guess.

## Output spec

Every delivered image is:

| Property | Value |
|---|---|
| Aspect ratio | 1:1, centre crop |
| Dimensions | 1000 × 1000 px |
| Resolution | 72 DPI |
| Format | JPEG (`.jpg`) |
| File size | under 1 MB (quality steps down from 85 until it fits) |
| Filename | source basename + `.jpg` (`IMG_0193.HEIC` → `IMG_0193.jpg`) |

## Step 1 — Resolve the folder ID

Extract the ID from the link. Both forms appear in the wild:

```
https://drive.google.com/drive/folders/<FOLDER_ID>
https://drive.google.com/open?id=<FOLDER_ID>&usp=drive_fs
```

If you only have a folder *name*, find it with `mcp__Google_Drive__search_files`:

```
title = '<name>' and mimeType = 'application/vnd.google-apps.folder'
```

**Names are frequently ambiguous** — this Drive has had three folders called `Extras`. When more than one matches, disambiguate by `parentId`: look up the intended parent folder first, then match. Never process a folder you are not certain about; confirm with the user instead.

## Step 2 — Enumerate the images

```
mcp__Google_Drive__search_files  →  query: parentId = '<FOLDER_ID>'  , pageSize: 50
```

Then:

- **Recurse into subfolders.** Any result with `mimeType = application/vnd.google-apps.folder` is a subfolder; enumerate it too and mirror its name as a subdirectory in the output. Folders in this Drive routinely nest one level (e.g. `Extras/Speaker with mic`).
- **Keep** `image/jpeg`, `image/png`, `image/webp`, `image/heif`, `image/heic`.
- **Skip** video (`video/quicktime`, `.MOV`), PDFs, and Google-native types. Say which files you skipped and why — never let a skip pass silently.
- **Watch for name collisions.** A `.png` and a `.webp` of the same photo both become `<stem>.jpg` and the second silently overwrites the first. When stems collide, keep the higher-resolution source and rename the other (e.g. `<stem>-webp.jpg`).

Report the inventory (count, formats, sizes) before downloading.

## Step 3 — Download each image

```
mcp__Google_Drive__download_file_content  →  fileId: <id>
```

Responses are far too large to return inline, so the harness writes each one to disk and reports the path. That is the **normal, expected** outcome — not an error. The file is JSON:

```json
{"content": "<base64>", "id": "...", "mimeType": "...", "title": "..."}
```

Collect the paths; `optimize.py` reads this shape directly. **Never `Read` or `cat` these files** — they are megabytes of base64 and will blow up the context. Pass the paths to the script and let Python do the decoding.

### The large-file wall

Files above roughly **6 MB fail with `MCP server session expired`**, consistently and unrecoverably. Retrying does not help.

**Fallback rule: after 3 consecutive session expiries, stop retrying and report.** Do not grind through a long retry loop. Name the files that failed, with their sizes and IDs, and point the user at the local fallback (below).

## Step 4 — Optimize

```bash
pip install -q pillow-heif   # once per session; required for iPhone HEIC files
python3 .claude/skills/web-ready-images/optimize.py \
    /tmp/web_ready/<subfolder> <downloaded_path> [<downloaded_path> ...]
```

`optimize.py` handles EXIF orientation, HEIC decoding, the centre crop, the resize, and the quality ladder. It prints one line per file and skips anything unreadable or under 200 px rather than dying mid-run.

Mirror the Drive subfolder structure under the output directory.

## Step 5 — Create the `web optimized` folder in Drive

```
mcp__Google_Drive__create_file
    title: "web optimized"
    contentMimeType: "application/vnd.google-apps.folder"
    parentId: <FOLDER_ID>          ← the SOURCE folder, so it nests inside
```

Check first whether a `web optimized` folder already exists in that parent (`search_files` with `title = 'web optimized' and parentId = '<FOLDER_ID>'`) and reuse it rather than creating a duplicate.

## Step 6 — Deliver

**Uploading the optimized images into that folder cannot be automated.** `create_file` accepts image bytes only as a `base64Content` *parameter*, which means the whole payload has to be emitted as model output. A 1000×1000 JPEG is 150–500 KB of base64 — 50,000 to 170,000 output tokens per image — which exceeds the output limit. There is no streaming, chunked, or resumable upload in the Drive MCP tool set, and no Drive credentials in the environment for a direct API call. Subagents do not solve it either: the ceiling is per-response output, and each subagent hits the same wall. This has been tested and confirmed; do not burn turns rediscovering it.

Only trivially small images (a few tens of KB) can actually be uploaded this way, which is not useful for real photos.

So:

1. ZIP the output directory, preserving subfolders.
2. Send it with `SendUserFile`.
3. Tell the user plainly: the `web optimized` folder is waiting in Drive at `<viewUrl>`, and they drag the ZIP contents into it. One drag, and the result matches what they asked for.

Do not describe the upload as done. Do not silently fall back to the ZIP without saying why.

## Local fallback for oversized files

For anything that hit the 6 MB wall, the user runs the same script on their own machine against the Drive-synced folder — no size limit there:

```bash
python3 optimize.py \
    "/Volumes/GoogleDrive/My Drive/<path>/web optimized" \
    "/Volumes/GoogleDrive/My Drive/<path>/<big file>"
```

Writing straight into the synced `web optimized` folder makes Drive do the upload.

## Failure modes

| Symptom | Cause | Action |
|---|---|---|
| `MCP server session expired` | file over ~6 MB | 3 strikes then stop; report file + size + ID |
| `ModuleNotFoundError: pillow_heif` | HEIC support missing | `pip install -q pillow-heif` |
| Output much larger than expected | source was already small; upscaled to 1000 px | fine — flag it if the source was under 1000 px |
| Two sources collapse to one output | `.png`/`.webp` stem collision | keep the higher-res one, rename the other |
| Portrait photo cropped along the wrong axis | EXIF orientation ignored | `optimize.py` already calls `exif_transpose`; make sure you used the script |
| Folder name matches several folders | ambiguous title | disambiguate by `parentId`; ask if still unclear |

## Reporting

Close with a short table: every source file, its status (done / skipped / failed), and the reason for anything not done. Give totals and the ZIP size. If any file failed, the user needs to know exactly which ones without opening the ZIP to work it out.
