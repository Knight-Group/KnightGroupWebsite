#!/usr/bin/env python3
"""Remove obsolete meta keywords tags from public HTML (Google ignores since 2009)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"scripts", "legacy", "Chess-Game-main", "admin", "node_modules", ".venv", "seo"}
PATTERN = re.compile(r"\s*<meta name=\"keywords\" content=\"[^\"]*\">\s*\n?", re.I)


def main() -> int:
    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        cleaned = PATTERN.sub("\n", text)
        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")
            updated += 1
            print(f"removed keywords: {path.relative_to(ROOT)}")
    print(f"Done. {updated} files updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
