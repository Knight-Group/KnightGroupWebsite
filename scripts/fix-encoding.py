#!/usr/bin/env python3
"""Fix common UTF-8 mojibake sequences across Knight Group HTML and JSON files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "screenshots"}
SCAN_SUFFIXES = {".html", ".json", ".txt", ".md"}

REPLACEMENTS = [
    ("â€”", "\u2014"),
    ("â€“", "\u2013"),
    ("â€˜", "'"),
    ("â€™", "'"),
    ("â€œ", '"'),
    ("â€\x9d", '"'),
    ("â€\x9c", '"'),
    ("â€¦", "\u2026"),
    ("ï¿½", "\u2014"),
    ("1ï¿½2", "1\u20132"),
    ("warranty responsibility ? well", "warranty responsibility \u2014 well"),
    ("professionallyâ€”with", "professionally\u2014with"),
    ("Knight Group â€” registered", "Knight Group \u2014 registered"),
]


def fix_text(text: str) -> str:
    em_dash = "\u2014"
    en_dash = "\u2013"
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(r"1[\ufffd]+2", f"1{en_dash}2", text)
    text = re.sub(r"(\w) \ufffd (\w)", lambda m: f"{m.group(1)} {em_dash} {m.group(2)}", text)
    text = re.sub(r"(\w)\ufffd(\w)", lambda m: f"{m.group(1)}{em_dash}{m.group(2)}", text)
    text = re.sub(r"(\w) â€ (\w)", lambda m: f"{m.group(1)} {em_dash} {m.group(2)}", text)
    return text


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
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
