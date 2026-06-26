#!/usr/bin/env python3
"""Convert hero source images to WebP and build hero-panels manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "hero images"
OUTPUT_DIR = ROOT / "Images" / "hero-panels"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"
SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
WEBP_QUALITY = 78
MAX_DIMENSION = 1400
SKIP_NAMES = {"desktop", "mobile", "placeholder"}
# PIL rotate() uses counter-clockwise degrees.
MANUAL_ROTATE = {
    "fixed.jpg": 90,
}


def slugify(name: str) -> str:
    stem = Path(name).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return stem or "hero-photo"


def prepare_image(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        rotate_deg = MANUAL_ROTATE.get(path.name.lower())
        if rotate_deg:
            image = image.rotate(rotate_deg, expand=True)
        if image.mode in ("RGBA", "LA", "P"):
            return image.convert("RGBA")
        return image.convert("RGB")


def convert_sources() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images: list[dict] = []

    if not SOURCE_DIR.is_dir():
        print(f"Warning: source folder missing: {SOURCE_DIR}")
        return images

    for path in sorted(SOURCE_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTS:
            continue
        if path.stem.lower() in SKIP_NAMES:
            continue

        slug = slugify(path.name)
        target = OUTPUT_DIR / f"{slug}.webp"
        if path.suffix.lower() == ".webp":
            if path.resolve() != target.resolve():
                target.write_bytes(path.read_bytes())
        else:
            needs_update = not target.is_file() or target.stat().st_mtime < path.stat().st_mtime
            if needs_update:
                image = prepare_image(path)
                width, height = image.size
                longest = max(width, height)
                if longest > MAX_DIMENSION:
                    scale = MAX_DIMENSION / longest
                    image = image.resize(
                        (max(1, int(width * scale)), max(1, int(height * scale))),
                        Image.Resampling.LANCZOS,
                    )
                image.save(target, "WEBP", quality=WEBP_QUALITY, method=6)

        images.append(
            {
                "src": f"/Images/hero-panels/{target.name}",
                "filename": target.name,
                "source": path.name,
            }
        )

    return images


def main() -> int:
    images = convert_sources()
    manifest = {
        "generated": True,
        "desktopCount": 4,
        "mobileCount": 2,
        "images": images,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(images)} hero panel image(s) to {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
