#!/usr/bin/env python3
"""Fail if obsolete meta keywords tags remain on public HTML."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", "legacy", "Chess-Game-main", "admin", "node_modules", ".venv", "seo"}
PATTERN = re.compile(r'<meta name="keywords"', re.I)


def main() -> int:
    hits: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if PATTERN.search(text):
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        print(f"meta keywords still present on {len(hits)} file(s):")
        for rel in hits[:30]:
            print(f"  {rel}")
        if len(hits) > 30:
            print(f"  ... and {len(hits) - 30} more")
        return 1
    print("No meta keywords tags on public HTML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
