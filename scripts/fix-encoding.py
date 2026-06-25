#!/usr/bin/env python3
"""Fix common UTF-8 mojibake sequences across Knight Group HTML files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "screenshots"}

REPLACEMENTS = [
    ("ï¿½", "—"),
    ("1ï¿½2", "1–2"),
    ("\ufffd", "—"),
]


def fix_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(r"Yes — ", "Yes — ", text)
    return text


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.parts[-2:] == ("scripts", path.name) and path.name.startswith("legacy-"):
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"fixed: {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} files updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
