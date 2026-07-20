#!/usr/bin/env python3
"""Carousel: serve only 640w (drop full-size 1200w srcset) so retina can't pull originals."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PERF = "20260720-carousel640"

# Full carousel <img ... data-kg-carousel-img="true">
IMG_RE = re.compile(
    r'<img\b[^>]*\bdata-kg-carousel-img="true"[^>]*>',
    re.I,
)


def rewrite_img(tag: str, index: int) -> str:
    # Extract filename stem from -640w.webp src (preferred) or from any GalleryImages src.
    m = re.search(
        r'src="/GalleryImages/([^"]+?)(?:-640w)?\.webp(?:\?v=[^"]*)?"',
        tag,
        re.I,
    )
    if not m:
        return tag
    stem = m.group(1)
    if stem.endswith("-640w"):
        stem = stem[: -len("-640w")]

    alt_m = re.search(r'\balt="([^"]*)"', tag)
    alt = alt_m.group(1) if alt_m else ""
    loading = "eager" if index < 3 else "lazy"

    return (
        f'<img src="/GalleryImages/{stem}-640w.webp?v={PERF}" '
        f'alt="{alt}" decoding="async" width="640" height="480" '
        f'data-kg-static="true" loading="{loading}" data-kg-carousel-img="true">'
    )


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    count = {"n": 0}

    def sub(m: re.Match[str]) -> str:
        i = count["n"]
        count["n"] += 1
        return rewrite_img(m.group(0), i)

    html, n = IMG_RE.subn(sub, html)
    print(f"rewrote carousel imgs: {n}")

    # Bump homepage asset versions.
    for old in (
        "20260719-perf",
        "20260719-map-restore",
        "20260719-intent-strip",
        "20260701-perf",
        "20260701-unified-includes",
    ):
        html = html.replace(old, PERF)

    INDEX.write_text(html, encoding="utf-8")
    sample = IMG_RE.search(html)
    print("sample:", sample.group(0)[:180] if sample else "none")
    print("1200w left:", html.count("1200w"))
    print(f"wrote {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
