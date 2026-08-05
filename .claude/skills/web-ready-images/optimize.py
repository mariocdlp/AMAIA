#!/usr/bin/env python3
"""Turn raw photos into web-ready images: 1:1 centre crop, 1000x1000, 72 DPI, JPEG.

Reads either MCP download-result JSON files (schema:
{content, id, mimeType, title} where `content` is base64) or plain image files,
and writes optimised JPEGs to an output directory.

Usage:
    python3 optimize.py OUTDIR INPUT [INPUT ...]
    python3 optimize.py --max-bytes 90000 OUTDIR INPUT [INPUT ...]

INPUT may be an MCP tool-result .txt/.json file or an ordinary image file.
"""

import argparse
import base64
import io
import json
import sys
from pathlib import Path

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:  # HEIC/HEIF support is required for iPhone photos
    sys.stderr.write("warning: pillow-heif missing; HEIC files will fail. "
                     "Install with: pip install pillow-heif\n")

from PIL import Image

EDGE = 1000
DPI = (72, 72)
MIN_EDGE = 200  # below this an image is a spacer/icon, not content


def load(path):
    """Return (name, image_bytes) from an MCP result file or a raw image file."""
    path = Path(path)
    raw = path.read_bytes()
    if raw[:1] in (b"{", b"["):  # MCP download result, not an image
        payload = json.loads(raw)
        return payload["title"], base64.b64decode(payload["content"])
    return path.name, raw


def optimize(data, name, outdir, max_bytes):
    try:
        img = Image.open(io.BytesIO(data))
    except Exception as exc:
        print(f"SKIP {name}: unreadable ({exc})")
        return None

    # EXIF orientation must be applied before cropping or portrait shots
    # get cropped along the wrong axis.
    try:
        from PIL import ImageOps

        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) < MIN_EDGE:
        print(f"SKIP {name}: too small ({w}x{h})")
        return None

    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((EDGE, EDGE), Image.LANCZOS)

    quality = 85
    while True:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", dpi=DPI, quality=quality, optimize=True)
        if buf.tell() <= max_bytes or quality <= 30:
            break
        quality -= 5

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / (Path(name).stem + ".jpg")
    outpath.write_bytes(buf.getvalue())
    print(f"OK {name} {w}x{h} -> {outpath.name} "
          f"{buf.tell() // 1024}KB q{quality}")
    return outpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--max-bytes", type=int, default=990_000,
                    help="shrink quality until the JPEG fits under this size")
    args = ap.parse_args()

    written = 0
    for src in args.inputs:
        try:
            name, data = load(src)
        except Exception as exc:
            print(f"SKIP {src}: could not load ({exc})")
            continue
        if optimize(data, name, args.outdir, args.max_bytes):
            written += 1
    print(f"\n{written}/{len(args.inputs)} written to {args.outdir}")


if __name__ == "__main__":
    main()
