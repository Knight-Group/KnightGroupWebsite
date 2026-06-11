#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "20260611-wave-a11y"
SKIP = {"scripts", "PolicyPages", "node_modules", ".git"}

patterns = [
    (re.compile(r"(kg-redesign\.css\?v=)[^\"']+"), rf"\g<1>{VERSION}"),
    (re.compile(r"(header\.min\.css\?v=)[^\"']+"), rf"\g<1>{VERSION}"),
    (re.compile(r"(includes(?:\.min)?\.js\?v=)[^\"']+"), rf"\g<1>{VERSION}"),
]

for path in sorted(ROOT.rglob("*.html")):
    if any(part in SKIP for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    updated = text
    for pattern, repl in patterns:
        updated = pattern.sub(repl, updated)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        print(path.relative_to(ROOT))
