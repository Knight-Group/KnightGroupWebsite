#!/usr/bin/env python3
"""Fail if any HTML references image files missing on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_RE = re.compile(r'src="([^"]+)"', re.I)
SKIP_PREFIXES = ("http://", "https://", "//", "data:", "tel:", "mailto:", "#")


def normalize_src(src: str) -> str | None:
    raw = src.split("?")[0].strip()
    if not raw or raw.startswith(SKIP_PREFIXES):
        return None
    rel = raw.lstrip("/")
    while rel.startswith("../"):
        rel = rel[3:]
    if rel.lower().startswith("galleryimages/"):
        rel = "GalleryImages/" + rel.split("/", 1)[1]
    if rel.lower().startswith("images/"):
        rel = "Images/" + rel.split("/", 1)[1]
    if not (rel.startswith("GalleryImages/") or rel.startswith("Images/")):
        return None
    return rel


def main() -> int:
    missing: list[tuple[str, str]] = []
    for html in ROOT.rglob("*.html"):
        if any(part in html.parts for part in ("node_modules", "scripts", ".git")):
            continue
        text = html.read_text(encoding="utf-8", errors="ignore")
        for match in SRC_RE.finditer(text):
            rel = normalize_src(match.group(1))
            if not rel:
                continue
            if not (ROOT / rel.replace("/", "\\")).is_file():
                missing.append((str(html.relative_to(ROOT)), rel))

    if missing:
        print(f"Missing image refs: {len(missing)}")
        seen: set[str] = set()
        for path, rel in missing:
            key = rel
            if key in seen:
                continue
            seen.add(key)
            print(f"  {rel}")
            for path, rel2 in missing:
                if rel2 == rel:
                    print(f"    <- {path}")
        return 1

    print("Missing image refs: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
