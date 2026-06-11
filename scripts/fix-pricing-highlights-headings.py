#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = "<h4>Why homeowners choose Knight Group</h4>"
NEW = "<h3>Why homeowners choose Knight Group</h3>"

for path in sorted((ROOT / "Services").glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if OLD not in text:
        continue
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"Updated {path.name}")
