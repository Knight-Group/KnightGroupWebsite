#!/usr/bin/env python3
"""Add meaningful alt text to Knight Group HTML images."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"legacy", "__pycache__", "scripts"}

LOGO_ALT = "Knight Group Handyman Services logo"
LIGHTBOX_ALT = "Knight Group handyman project photo"

SERVICE_FILE_ALTS = {
    "handyman": "Handyman services project photo",
    "general-repairs": "General repairs project photo",
    "plumbing-services": "Plumbing services project photo",
    "electrical-work": "Electrical fixture project photo",
    "carpentry-framing": "Carpentry and framing project photo",
    "painting-finishing": "Painting and finishing project photo",
    "home-renovations": "Home renovation project photo",
    "doors-windows": "Doors and windows project photo",
    "custom-projects": "Custom handyman project photo",
    "emergency-services": "Emergency handyman repair project photo",
}

INDEX_CARD_ALTS = {
    "general-repairs": "General repairs service background photo",
    "kg-leaky-pipes": "Plumbing services background photo",
    "KG-fixture": "Electrical fixture service background photo",
    "carpentry-framing": "Carpentry and framing service background photo",
    "painting-finishing": "Painting and finishing service background photo",
    "home-renovations": "Home renovations service background photo",
    "kg-door-window-repair": "Doors and windows service background photo",
    "custom-projects": "Custom projects service background photo",
    "kg-waterheater-pipe-burst": "Emergency handyman service background photo",
}


def set_alt(tag: str, alt: str) -> str:
    if re.search(r'\balt\s*=\s*["\']', tag, re.I):
        return re.sub(r'\balt\s*=\s*["\'][^"\']*["\']', f'alt="{alt}"', tag, count=1, flags=re.I)
    return tag[:-1] + f' alt="{alt}">'


def service_alt_from_src(src: str) -> str | None:
    for slug, alt in SERVICE_FILE_ALTS.items():
        if slug in src.replace("\\", "/"):
            return alt
    return None


def index_card_alt_from_src(src: str) -> str | None:
    for key, alt in INDEX_CARD_ALTS.items():
        if key in src:
            return alt
    return None


def fix_html(html: str) -> tuple[str, int]:
    changes = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal changes
        tag = match.group(0)
        src_match = re.search(r'\bsrc\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        src = src_match.group(1) if src_match else ""

        if "KnightGroupLogo" in src:
            new_tag = set_alt(tag, LOGO_ALT)
        elif "gallery-lightbox-img" in tag:
            new_tag = set_alt(tag, LIGHTBOX_ALT)
        elif "handyman.jpg" in src:
            new_tag = set_alt(tag, "Knight Group handyman services in Pinellas County, Florida")
        elif "FB-KG-Brochure1" in src:
            new_tag = set_alt(tag, "Knight Group Handyman Services brochure")
        elif "kg-service-card__bg" in tag:
            alt = index_card_alt_from_src(src) or "Knight Group handyman service photo"
            new_tag = set_alt(tag, alt)
        elif "/Images/services/" in src or "Images/services/" in src:
            alt = service_alt_from_src(src) or "Knight Group handyman service photo"
            new_tag = set_alt(tag, alt)
        else:
            alt_match = re.search(r'\balt\s*=\s*["\']([^"\']*)["\']', tag, re.I)
            if alt_match and alt_match.group(1).strip():
                return tag
            new_tag = set_alt(tag, "Knight Group handyman project photo")

        if new_tag != tag:
            changes += 1
        return new_tag

    updated = re.sub(r"<img\b[^>]*>", replacer, html, flags=re.I)
    return updated, changes


def main() -> int:
    total = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        updated, changes = fix_html(original)
        if not changes:
            continue
        path.write_text(updated, encoding="utf-8")
        total += changes
        print(f"updated {path.relative_to(ROOT)} ({changes} images)")
    print(f"Done. {total} image alt updates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
