#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = sorted(ROOT.glob("*-handyman.html"))
openings: list[str] = []
metas: list[str] = []
heroes: list[str] = []

for page in pages:
    text = page.read_text(encoding="utf-8")
    if m := re.search(r'<meta name="description" content="([^"]+)"', text):
        metas.append(m.group(1))
    if m := re.search(r'class="kg-page-hero__lead">([^<]+)', text):
        heroes.append(m.group(1))
    if m := re.search(r"<h2>Handyman services in [^<]+</h2>\s*<p>([^<]+)", text):
        openings.append(m.group(1)[:140])

print(f"City pages: {len(pages)}")
print(f"Unique meta descriptions: {len(set(metas))} / {len(metas)}")
print(f"Unique hero leads: {len(set(heroes))} / {len(heroes)}")
print(f"Unique openings: {len(set(openings))} / {len(openings)}")

old_opening = "Knight Group Handyman Services LLC provides registered, insured handyman work"
old_scope = "Every job stays within handyman scope. If a repair requires"
old_faq = "Common questions homeowners ask before booking this type of work in Pinellas County"
for label, phrase in [
    ("old opening boilerplate", old_opening),
    ("old scope boilerplate", old_scope),
    ("wrong Pinellas FAQ on Tampa", old_faq),
]:
    hits = [p.name for p in pages if phrase in p.read_text(encoding="utf-8")]
    print(f"{label}: {len(hits)} hits")

tampa = (ROOT / "tampa-handyman.html").read_text(encoding="utf-8")
print("Tampa has Hillsborough FAQ:", "Hillsborough County.</p>" in tampa)
print("Tampa sidebar county:", "Hillsborough County coverage" in tampa)
print("Tampa gallery Hillsborough alt:", "Hillsborough County FL" in tampa)
