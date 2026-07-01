#!/usr/bin/env python3
"""Fail if any HTML references a GalleryImages file that is missing on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "GalleryImages"
IMG_RE = re.compile(r'src="([^"]*GalleryImages/[^"]+)"', re.I)


def main() -> int:
    missing: list[tuple[str, str]] = []
    for html in ROOT.rglob("*.html"):
        if "node_modules" in html.parts or "scripts" in html.parts:
            continue
        text = html.read_text(encoding="utf-8", errors="ignore")
        for match in IMG_RE.finditer(text):
            src = match.group(1).split("?")[0]
            rel = unquote(src.replace("../", "").lstrip("/"))
            if rel.lower().startswith("galleryimages/"):
                rel = "GalleryImages/" + rel.split("/", 1)[1]
            if not (ROOT / rel).is_file():
                missing.append((str(html.relative_to(ROOT)), src))

    empty_figures = 0
    figure_re = re.compile(
        r'<figure class="kg-service-gallery__item">\s*</figure>',
        re.I | re.S,
    )
    for html in ROOT.rglob("*.html"):
        if "node_modules" in html.parts or "scripts" in html.parts:
            continue
        text = html.read_text(encoding="utf-8", errors="ignore")
        empty_figures += len(figure_re.findall(text))

    if missing:
        print(f"Missing gallery refs: {len(missing)}")
        for path, src in missing[:50]:
            print(f"  {path} -> {src}")
    else:
        print("Missing gallery refs: 0")

    print(f"Empty gallery figures: {empty_figures}")
    return 1 if missing or empty_figures else 0


if __name__ == "__main__":
    raise SystemExit(main())
