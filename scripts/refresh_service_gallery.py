#!/usr/bin/env python3
"""Re-embed inline gallery images on migrated service pages."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from refresh_inline_galleries import refresh_page  # noqa: E402

ROOT = SCRIPT_DIR.parent
SERVICES = ROOT / "Services"


def refresh_slug(slug: str) -> None:
    path = SERVICES / f"{slug}.html"
    if not refresh_page(path, slug, prefix="../"):
        raise SystemExit(f"could not refresh: {path}")


def main(argv: list[str]) -> int:
    slugs = argv[1:]
    if slugs:
        for slug in slugs:
            refresh_slug(slug)
        from audit_gallery_refs import main as audit_gallery_refs

        return audit_gallery_refs()

    from refresh_inline_galleries import main as refresh_all

    return refresh_all()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
