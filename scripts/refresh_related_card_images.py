#!/usr/bin/env python3
"""Refresh related-card images in generated HTML. Does not rewrite titles, metas, or prose."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from service_related import rewrite_related_grids  # noqa: E402

VERSION = "20260912-related-cards"


def main() -> int:
    changed = 0
    for html_path in sorted(ROOT.rglob("*.html")):
        if any(part in html_path.parts for part in ("node_modules", "scripts", ".git")):
            continue
        text = html_path.read_text(encoding="utf-8")
        if "kg-service-related-grid" not in text:
            continue
        updated = rewrite_related_grids(text, version=VERSION)
        updated = re.sub(
            r'(href="(?:\.\./)?/?CSS/kg-redesign\.css)\?v=[^"]+"',
            rf'\1?v={VERSION}"',
            updated,
        )
        if updated != text:
            html_path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Updated related-card images on {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
