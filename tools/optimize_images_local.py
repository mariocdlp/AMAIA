#!/usr/bin/env python3
"""
Optimize images in a local folder (e.g. Google Drive mounted on your Mac).

Requirements:
    pip install Pillow

Usage:
    python3 optimize_images_local.py "/path/to/folder"

Example (Google Drive on Mac):
    python3 optimize_images_local.py "/Users/yourname/Library/CloudStorage/GoogleDrive-mariochow@gmail.com/My Drive/Fiesta TEnts/Inventory"

What it does:
  - Walks all subfolders recursively
  - For each image: center-crops to 1:1, resizes to 1000x1000, sets DPI to 72, saves as JPEG < 1 MB
  - Saves processed files into a "web-ready" subfolder alongside the originals
  - Skips SVGs, tiny images, and already-processed files
"""

import sys
import io
from pathlib import Path
from PIL import Image

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
SKIP_MIME = {".svg"}
TARGET_SIZE = (1000, 1000)
TARGET_DPI = (72, 72)
MAX_BYTES = 990_000


def process_image(src: Path, dst: Path):
    try:
        img = Image.open(src).convert("RGB")
    except Exception as e:
        print(f"  ⚠  Cannot open {src.name}: {e}")
        return False

    w, h = img.size
    if max(w, h) < 500:
        print(f"  ⏭  {src.name} — too small ({w}x{h}), skipping")
        return False

    # Center crop to 1:1
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize to 1000×1000
    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    # Compress to < 1 MB
    quality = 85
    buf = io.BytesIO()
    while quality >= 20:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", dpi=TARGET_DPI, quality=quality, optimize=True)
        if buf.tell() < MAX_BYTES:
            break
        quality -= 5

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(buf.getvalue())
    print(f"  ✓  {src.name}  ({w}x{h} → 1000x1000, {buf.tell()//1024} KB, q={quality})")
    return True


def process_folder(folder: Path, depth: int = 0):
    indent = "  " * depth
    web_ready = folder / "web-ready"

    images = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED
    ]

    if images:
        print(f"\n{indent}📁  {folder.name}  ({len(images)} images)")
        for img_path in sorted(images):
            dst = web_ready / (img_path.stem + ".jpg")
            if dst.exists():
                print(f"  ⏭  {img_path.name} — already processed, skipping")
                continue
            process_image(img_path, dst)

    for sub in sorted(folder.iterdir()):
        if sub.is_dir() and sub.name != "web-ready":
            process_folder(sub, depth + 1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 optimize_images_local.py \"/path/to/folder\"")
        print()
        print("Tip — find your Google Drive path on Mac:")
        print("  ls ~/Library/CloudStorage/")
        sys.exit(1)

    root = Path(sys.argv[1])
    if not root.exists():
        print(f"Folder not found: {root}")
        sys.exit(1)

    print(f"Processing: {root}")
    print("Optimized images will be saved in 'web-ready' subfolders.\n")
    process_folder(root)
    print("\n✅  Done!")


if __name__ == "__main__":
    main()
