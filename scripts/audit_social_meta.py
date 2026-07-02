#!/usr/bin/env python3
"""Find pages with incomplete Open Graph or Twitter card tags."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"scripts", "legacy", "admin", "node_modules", ".venv", "seo", "Chess-Game-main", "page-template.html"}

OG_REQUIRED = (
    "og:url",
    "og:title",
    "og:description",
    "og:image",
    "og:type",
)
TWITTER_REQUIRED = (
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
)


def main() -> int:
    failures = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        html = path.read_text(encoding="utf-8", errors="ignore")
        missing_og = [tag for tag in OG_REQUIRED if tag not in html]
        missing_tw = [tag for tag in TWITTER_REQUIRED if tag not in html]
        if missing_og or missing_tw:
            failures += 1
            print(f"INCOMPLETE {rel}")
            if missing_og:
                print(f"  missing og: {', '.join(missing_og)}")
            if missing_tw:
                print(f"  missing twitter: {', '.join(missing_tw)}")
    if not failures:
        print("All public HTML pages have complete OG and Twitter tags.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
