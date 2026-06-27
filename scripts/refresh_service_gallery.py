#!/usr/bin/env python3
"""Re-embed inline gallery images on migrated service pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_pool import SERVICE_PARENT_TO_CATEGORY, prose_with_inline_gallery  # noqa: E402

ROOT = SCRIPT_DIR.parent
SERVICES = ROOT / "Services"

PROSE_BLOCK = re.compile(
    r'(<div class="kg-service-prose">\s*)(.*?)(\s*</div>\s*\n?\s*<aside class="kg-service-sidebar")',
    re.S,
)
FIGURE = re.compile(r"\n<figure class=\"kg-prose-photo.*?</figure>\s*", re.S)


def clean_prose(prose: str) -> str:
    prose = FIGURE.sub("", prose)
    prose = re.sub(r"(<h[1-6][^>]*>)\s*\?\?\s*", r"\1", prose)
    prose = re.sub(r"\?\?\s*Safety First", "Safety First", prose)
    prose = re.sub(r"\ufffd+", "", prose)
    prose = re.sub(r'<div class="warning-box">', '<div class="kg-service-callout">', prose)
    return prose.strip()


def refresh_slug(slug: str) -> None:
    path = SERVICES / f"{slug}.html"
    if not path.is_file():
        raise SystemExit(f"missing page: {path}")

    html = path.read_text(encoding="utf-8")
    match = PROSE_BLOCK.search(html)
    if not match:
        raise SystemExit(f"no prose block in {path.name}")

    prose = clean_prose(match.group(2))
    prose = prose_with_inline_gallery(
        prose,
        slug,
        "../",
        category=SERVICE_PARENT_TO_CATEGORY.get(slug),
        alt_fallback=f"{slug.replace('-', ' ')} project photo in Pinellas County",
    )
    updated = html[: match.start(2)] + "\n" + prose + "\n                        " + html[match.end(2) :]
    path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"refreshed gallery: {path.name}")


def main(argv: list[str]) -> int:
    slugs = argv[1:] or ["electrical-work"]
    for slug in slugs:
        refresh_slug(slug)
    from audit_gallery_refs import main as audit_gallery_refs

    return audit_gallery_refs()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
