#!/usr/bin/env python3
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "Services"
for path in sorted(root.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<div class="pricing-highlights">(.*?)</div>', text, re.S)
    if match:
        print(path.name, match.group(1)[:180].replace("\n", " "))
