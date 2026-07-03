#!/usr/bin/env python3
"""Quick audit of niche service page word counts and structure."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICES = ROOT / "Services"

def analyze(path: Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    prose_match = re.search(r'<div class="kg-service-prose">(.*?)</div>\s*\n?\s*<aside', html, re.S)
    prose = prose_match.group(1) if prose_match else ""
    text = re.sub(r"<[^>]+>", " ", prose)
    text = re.sub(r"\s+", " ", text).strip()
    words = len(text.split()) if text else 0
    h2 = len(re.findall(r"<h2", prose))
    h3 = len(re.findall(r"<h3", prose))
    ul = len(re.findall(r"<ul", prose))
    faq = len(re.findall(r"<details class=\"kg-faq-item\"", html))
    photos = len(re.findall(r"kg-prose-photo", prose))
    return {"words": words, "h2": h2, "h3": h3, "ul": ul, "faq": faq, "photos": photos}

plumbing = analyze(SERVICES / "plumbing-services.html")
print(f"plumbing-services: {plumbing}")

niche_files = sorted(SERVICES.glob("*.html"))
niche_slugs = [
    "home-repair-near-me", "small-jobs", "small-job-carpenter", "sink-faucet-repair",
    "drywall-repair", "sliding-door-repair", "drywall-paint-repair", "water-damage-repair",
    "screen-door-repair", "trim-repair", "faucet-replacement", "toilet-repair",
    "garbage-disposal-replacement", "shutoff-valve-repair", "drain-unclogging",
    "hole-in-wall-repair", "caulking-repair", "mobile-home-repairs", "custom-shelving",
    "cabinet-repair", "door-frame-repair", "door-adjustment", "window-screen-repair",
    "interior-painting", "texture-matching", "trim-painting",
]

thin = []
for slug in niche_slugs:
    stats = analyze(SERVICES / f"{slug}.html")
    print(f"{slug}: {stats}")
    if stats["words"] < 350:
        thin.append((slug, stats["words"]))

print(f"\nThin pages (<350 words): {thin}")
print(f"Average niche words: {sum(analyze(SERVICES / f'{s}.html')['words'] for s in niche_slugs) / len(niche_slugs):.0f}")
