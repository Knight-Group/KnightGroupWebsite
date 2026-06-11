#!/usr/bin/env python3
"""Replace baked header-include markup with an empty placeholder."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = (
    re.compile(
        r'<div id="header-include">.*?</div>\s*\n\s*(?=<nav class="kg-crawl-hub"|<main id="main-content")',
        re.S,
    ),
    re.compile(
        r'<div id="header-include">.*?</div>\s*\n\s*<main id="main-content"',
        re.S,
    ),
    re.compile(
        r'<div id="header-include">.*?</div>\s*\n\s*<div class="thank-you-container"',
        re.S,
    ),
)


def main() -> int:
    for name in (
        "galleries.html",
        "service-areas.html",
        "index.html",
        "thank-you.html",
    ):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated = text
        for pattern in PATTERNS:
            next_text = pattern.sub('<div id="header-include"></div>\n\n    ', updated, count=1)
            if next_text != updated:
                updated = next_text
                break
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"Stripped baked header from {name}")
        else:
            print(f"No baked header found in {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
