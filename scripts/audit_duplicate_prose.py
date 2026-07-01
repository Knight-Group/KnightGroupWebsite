#!/usr/bin/env python3
"""Find repeated sentences across niche service prose."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Services"
slugs = [
    "home-repair-near-me", "small-jobs", "faucet-replacement", "drywall-repair",
    "window-screen-repair", "toilet-repair",
]

def prose_text(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<div class="kg-service-prose">(.*?)</div>\s*\n?\s*<aside', html, re.S)
    prose = m.group(1) if m else ""
    text = re.sub(r"<[^>]+>", " ", prose)
    return re.sub(r"\s+", " ", text).strip()

sentences_by_slug = {}
all_sents = {}
for slug in sorted(p.name.replace(".html", "") for p in ROOT.glob("*.html")):
    if slug in {"index", "handcraftedfurniture&resins", "programming&databases"}:
        continue
    text = prose_text(ROOT / f"{slug}.html")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]
    sentences_by_slug[slug] = sents
    for s in sents:
        all_sents.setdefault(s.lower(), []).append(slug)

dupes = {s: pages for s, pages in all_sents.items() if len(pages) > 1}
print(f"Duplicate sentences across pages: {len(dupes)}")
for s, pages in sorted(dupes.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"\n[{len(pages)} pages] {s[:120]}...")
    print("  ->", ", ".join(pages[:8]), ("..." if len(pages) > 8 else ""))
