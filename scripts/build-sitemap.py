#!/usr/bin/env python3
"""Regenerate sitemap.xml from seo/page-manifest.json plus core static pages."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seo" / "page-manifest.json"
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://www.knightgroup.com"
TODAY = date.today().isoformat()

STATIC_PAGES = [
    ("/", "1.0", "weekly"),
    ("/booking", "0.95", "monthly"),
    ("/services", "0.92", "weekly"),
    ("/pricing", "0.88", "monthly"),
    ("/contact", "0.88", "monthly"),
    ("/about", "0.82", "monthly"),
    ("/galleries", "0.80", "weekly"),
    ("/service-areas", "0.85", "monthly"),
    ("/home-watch-pinellas", "0.90", "weekly"),
    ("/home-watch-pricing", "0.86", "monthly"),
    ("/home-watch-checklist", "0.84", "monthly"),
    ("/florida-snowbird-departure-checklist", "0.80", "monthly"),
    ("/property-manager-handyman", "0.86", "weekly"),
]

MAJOR_SERVICES = [
    "handyman",
    "general-repairs",
    "plumbing-services",
    "electrical-work",
    "carpentry-framing",
    "painting-finishing",
    "home-renovations",
    "doors-windows",
    "custom-projects",
    "emergency-services",
]


def _mtime_iso(path: Path) -> str | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def lastmod_for_loc(loc: str) -> str:
    """Use the HTML file date so Google does not see every URL as rewritten today."""
    rel = loc.replace(BASE, "").strip("/")
    candidates: list[Path] = []
    if not rel:
        candidates.append(ROOT / "index.html")
    elif rel == "galleries":
        candidates.append(ROOT / "galleries.html")
        candidates.extend((ROOT / "gallery").glob("*.html"))
    else:
        candidates.append(ROOT / f"{rel}.html")
    dates = [iso for path in candidates if (iso := _mtime_iso(path))]
    return max(dates) if dates else TODAY


def add_url(urlset: ET.Element, loc: str, priority: str, changefreq: str) -> None:
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = loc
    ET.SubElement(url, "lastmod").text = lastmod_for_loc(loc)
    ET.SubElement(url, "changefreq").text = changefreq
    ET.SubElement(url, "priority").text = priority


def main() -> int:
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    seen: set[str] = set()
    for path, priority, changefreq in STATIC_PAGES:
        loc = f"{BASE}{path if path != '/' else '/'}"
        if loc not in seen:
            add_url(urlset, loc, priority, changefreq)
            seen.add(loc)

    for slug in MAJOR_SERVICES:
        loc = f"{BASE}/Services/{slug}"
        if loc not in seen:
            add_url(urlset, loc, "0.86", "monthly")
            seen.add(loc)

    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for page in data.get("pages", []):
            loc = page.get("canonical") or f"{BASE}/{page['path'].replace('.html', '')}"
            if loc in seen:
                continue
            add_url(urlset, loc, page.get("priority", "0.75"), "monthly")
            seen.add(loc)

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(SITEMAP, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote {len(seen)} URLs to {SITEMAP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
