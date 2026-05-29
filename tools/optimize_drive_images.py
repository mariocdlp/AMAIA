#!/usr/bin/env python3
"""
Optimize Google Drive images for web use.

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib Pillow

Usage (first run will open a browser to authorize):
    python3 optimize_drive_images.py

What it does for each image:
  - Center-crops to 1:1 aspect ratio
  - Resizes to 1000x1000 px
  - Sets DPI to 72
  - Compresses as JPEG under 1 MB
  - Uploads to a "web-ready" subfolder in the same parent folder
"""

import io
import os
import tempfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from PIL import Image

# ── CONFIG ────────────────────────────────────────────────────────────────────

# Folder IDs to process (images at the top level of each folder AND in subfolders)
SOURCE_FOLDER_IDS = [
    "17WF4OZInThC0x8OdNyuYCvHEMfOMfM4J",   # main photos folder
    "1PjKXEWNp-DuRk2azlyn2L9Z93F6-HDBG",   # rentals folder (has subfolders)
]

SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"  # Download from Google Cloud Console

TARGET_SIZE = (1000, 1000)
TARGET_DPI = (72, 72)
MAX_BYTES = 990_000  # stay safely under 1 MB
SKIP_MIME = {"image/svg+xml"}  # SVGs don't need raster processing


# ── IMAGE PROCESSING ──────────────────────────────────────────────────────────

def process_image_bytes(data: bytes) -> bytes | None:
    """Return optimized JPEG bytes, or None if image is too small."""
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        print(f"    ⚠  Could not open image: {e}")
        return None

    w, h = img.size
    if max(w, h) < 500:
        print(f"    ⚠  Skipping – too small ({w}x{h}), would upscale badly")
        return None

    # Center crop to 1:1
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize to 1000×1000
    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    # Compress to <1 MB
    quality = 85
    while quality >= 20:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", dpi=TARGET_DPI, quality=quality, optimize=True)
        if buf.tell() < MAX_BYTES:
            break
        quality -= 5

    buf.seek(0)
    result = buf.read()
    print(f"    ✓  {w}x{h} → 1000x1000  {len(result)/1024:.0f} KB  q={quality}")
    return result


# ── DRIVE HELPERS ─────────────────────────────────────────────────────────────

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. Download it from:\n"
                    "  Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        f" and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]


def list_images(service, folder_id: str) -> list[dict]:
    """Return all image files directly inside folder_id."""
    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, size)",
        pageSize=100,
    ).execute()
    return results.get("files", [])


def list_subfolders(service, folder_id: str) -> list[dict]:
    query = (
        f"'{folder_id}' in parents"
        " and mimeType='application/vnd.google-apps.folder'"
        " and trashed=false"
    )
    results = service.files().list(
        q=query, fields="files(id, name)", pageSize=100
    ).execute()
    return results.get("files", [])


def download_file(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buf.seek(0)
    return buf.read()


def upload_file(service, name: str, data: bytes, parent_id: str) -> str:
    base_name = os.path.splitext(name)[0]
    upload_name = f"{base_name}.jpg"
    meta = {"name": upload_name, "parents": [parent_id]}
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="image/jpeg", resumable=True)
    f = service.files().create(body=meta, media_body=media, fields="id").execute()
    return f["id"]


# ── MAIN ──────────────────────────────────────────────────────────────────────

def process_folder(service, folder_id: str, folder_name: str, depth: int = 0):
    indent = "  " * depth
    images = list_images(service, folder_id)

    if not images:
        # Recurse into subfolders even if no images at this level
        for sub in list_subfolders(service, folder_id):
            process_folder(service, sub["id"], sub["name"], depth + 1)
        return

    web_ready_id = get_or_create_folder(service, "web-ready", folder_id)
    print(f"{indent}📁  {folder_name}  ({len(images)} images)")

    for img in images:
        if img.get("mimeType") in SKIP_MIME:
            print(f"{indent}  ⏭  {img['name']} (SVG – skipped)")
            continue

        size_kb = int(img.get("size", 0)) // 1024
        print(f"{indent}  ↓  {img['name']}  ({size_kb} KB)")
        try:
            raw = download_file(service, img["id"])
            optimized = process_image_bytes(raw)
            if optimized:
                upload_file(service, img["name"], optimized, web_ready_id)
        except Exception as e:
            print(f"{indent}  ✗  Error: {e}")

    # Recurse into subfolders (but not into the web-ready folder we just created)
    for sub in list_subfolders(service, folder_id):
        if sub["name"] == "web-ready":
            continue
        process_folder(service, sub["id"], sub["name"], depth + 1)


def main():
    print("Connecting to Google Drive…")
    service = get_drive_service()
    print("Connected.\n")

    for folder_id in SOURCE_FOLDER_IDS:
        meta = service.files().get(fileId=folder_id, fields="name").execute()
        process_folder(service, folder_id, meta.get("name", folder_id))

    print("\n✅  Done! Optimized images are in the 'web-ready' subfolders.")


if __name__ == "__main__":
    main()
