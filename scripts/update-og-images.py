#!/usr/bin/env python3
"""Update Open Graph and Twitter card images across Knight Group HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.knightgroup.com/Images"
OG_CLEAN = f"{BASE}/knightgroup-og-card-1200x630-clean.png"
OG_PHONE = f"{BASE}/knightgroup-og-card-1200x630-phone.png"
OG_SQUARE = f"{BASE}/knightgroup-social-square-1200x1200-phone.png"
OG_TWITTER = f"{BASE}/knightgroup-twitter-card-1200x628-phone.png"
DEFAULT_ALT = "Knight Group handyman services in Pinellas County, Florida"

OG_IMAGE_TAG = re.compile(
    r"\s*<meta property=\"og:image(?:[:a-z]+)?\" content=\"[^\"]*\">",
    re.I,
)
TWITTER_IMAGE = re.compile(
    r"\s*<meta name=\"twitter:image\" content=\"[^\"]*\">",
    re.I,
)
OG_DESCRIPTION = re.compile(
    r'(<meta property="og:description" content="[^"]*">)',
    re.I,
)


def build_og_images_block(alt: str) -> str:
    return (
        f'\n    <meta property="og:image" content="{OG_CLEAN}">\n'
        f'    <meta property="og:image:width" content="1200">\n'
        f'    <meta property="og:image:height" content="630">\n'
        f'    <meta property="og:image:alt" content="{alt}">\n'
        f'    <meta property="og:image" content="{OG_PHONE}">\n'
        f'    <meta property="og:image:width" content="1200">\n'
        f'    <meta property="og:image:height" content="630">\n'
        f'    <meta property="og:image" content="{OG_SQUARE}">\n'
        f'    <meta property="og:image:width" content="1200">\n'
        f'    <meta property="og:image:height" content="1200">\n'
    )


def update_html(html: str) -> tuple[str, bool]:
    if "og:description" not in html and "og:image" not in html:
        return html, False

    alt_match = re.search(
        r'<meta property="og:image:alt" content="([^"]*)"',
        html,
        re.I,
    )
    alt = alt_match.group(1) if alt_match else DEFAULT_ALT

    updated = OG_IMAGE_TAG.sub("", html)
    if updated == html and "og:description" not in html:
        return html, False

    desc_match = OG_DESCRIPTION.search(updated)
    if not desc_match:
        return html, False

    updated = (
        updated[: desc_match.end()]
        + build_og_images_block(alt)
        + updated[desc_match.end() :]
    )
    updated = TWITTER_IMAGE.sub(
        f'\n    <meta name="twitter:image" content="{OG_TWITTER}">',
        updated,
        count=1,
    )
    return updated, updated != html


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if path.parent.name == "scripts":
            continue
        original = path.read_text(encoding="utf-8")
        updated, did_change = update_html(original)
        if not did_change:
            continue
        path.write_text(updated, encoding="utf-8")
        changed += 1
        print(f"updated: {path.relative_to(ROOT)}")
    print(f"Done. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
