#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "PolicyPages", "node_modules", ".git"}

for path in sorted(ROOT.rglob("*.html")):
    if any(part in SKIP for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    marker = '<div id="header-include">'
    if marker not in text:
        continue
    after = text.split(marker, 1)[1]
    if after.lstrip().startswith("</div>"):
        print(f"EMPTY: {path.relative_to(ROOT)}")
    elif "<!-- Header -->" in after[:500]:
        print(f"BAKED: {path.relative_to(ROOT)}")
