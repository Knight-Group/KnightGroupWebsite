#!/usr/bin/env python3
"""Point ImageObject.url at gallery detail pages instead of raw /GalleryImages/ assets."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERIES = ROOT / "galleries.html"
BASE = "https://www.knightgroup.com"

# Image filename in ImageObject.url -> gallery detail page path.
IMAGE_FILE_TO_PAGE: dict[str, str] = {
    "before-after-ac-filter-replacement-and-cleaning.webp": "/gallery/filter-change-before-after",
    "before-after-ac-vent-filter-change.webp": "/gallery/ac-vent-filter-change-before-after",
    "Refinished Bathroom_Window.webp": "/gallery/bathroom-tub-window-remodel",
    "before-after-broken-blinds-replaced.webp": "/gallery/blinds-replacement-before-after",
    "before-after-carpet-removal.webp": "/gallery/carpet-removal-before-after",
    "Refinished_Bathroom.webp": "/gallery/bathroom-remodel-cobblestone",
    "before-after-curtain-rod-mount.webp": "/gallery/curtain-rod-mount-before-after",
    "before-after-door-lock.webp": "/gallery/door-lock-repair-before-after",
    "before-after-door-wedge.webp": "/gallery/door-wedge-before-after",
    "before-after-fire-extinguisher-mount.webp": "/gallery/fire-extinguisher-mount-before-after",
    "GarbageDisposal.webp": "/gallery/garbage-disposal-install",
    "before-after-copeland-morgan-llc-work-order.webp": "/galleries#image-copeland-morgan-llc-work-order-before-after",
}


def main() -> int:
    text = GALLERIES.read_text(encoding="utf-8")
    updated = 0
    for filename, page_path in IMAGE_FILE_TO_PAGE.items():
        old = f'"url": "{BASE}/GalleryImages/{filename}"'
        new = f'"url": "{BASE}{page_path}"'
        if old in text:
            text = text.replace(old, new)
            updated += 1
    GALLERIES.write_text(text, encoding="utf-8")
    print(f"Updated {updated} ImageObject url field(s) in {GALLERIES.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
