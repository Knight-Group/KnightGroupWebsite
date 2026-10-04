#!/usr/bin/env python3
"""Regenerate sitemap.xml from seo/page-manifest.json plus core static pages."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import date
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
    ("/home-watch-sample-report", "0.82", "monthly"),
    ("/florida-snowbird-departure-checklist", "0.80", "monthly"),
    ("/property-manager-handyman", "0.86", "weekly"),
    ("/join", "0.40", "monthly"),
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


LASTMOD_STATE = ROOT / "seo" / "sitemap-lastmod.json"
_state: dict[str, dict[str, str]] | None = None
_state_dirty = False
_git_ok: bool | None = None


def _load_state() -> dict[str, dict[str, str]]:
    global _state
    if _state is None:
        try:
            _state = json.loads(LASTMOD_STATE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _state = {}
    return _state


def _content_hash(paths: list[Path]) -> str | None:
    """Hash page text with whitespace-only differences removed (CRLF, blank lines)."""
    digest = hashlib.sha256()
    found = False
    for path in paths:
        if not path.is_file():
            continue
        found = True
        text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        lines = [line.rstrip() for line in text.split("\n")]
        digest.update("\n".join(line for line in lines if line).encode("utf-8"))
    return digest.hexdigest() if found else None


def _git_available() -> bool:
    global _git_ok
    if _git_ok is None:
        try:
            shallow = subprocess.run(
                ["git", "rev-parse", "--is-shallow-repository"],
                cwd=ROOT, capture_output=True, text=True, check=True,
            ).stdout.strip()
            _git_ok = shallow == "false"
        except (OSError, subprocess.CalledProcessError):
            _git_ok = False
    return _git_ok


def _git_date(path: Path) -> str | None:
    if not _git_available():
        return None
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def lastmod_for_loc(loc: str) -> str:
    """Content-based lastmod.

    The date only moves when the page text really changes (tracked by hash in
    seo/sitemap-lastmod.json). File mtimes and build dates are ignored, so
    fresh checkouts and automated gallery publishes no longer mark every URL
    as modified today. New pages are seeded from git history when available.
    """
    global _state_dirty
    rel = loc.replace(BASE, "").strip("/")
    if not rel:
        paths = [ROOT / "index.html"]
    elif rel == "galleries":
        paths = [ROOT / "galleries.html"]
    else:
        paths = [ROOT / f"{rel}.html"]
    digest = _content_hash(paths)
    if digest is None:
        return TODAY
    state = _load_state()
    entry = state.get(loc)
    if entry and entry.get("sha256") == digest and entry.get("lastmod"):
        return entry["lastmod"]
    if entry:
        lastmod = TODAY
    else:
        lastmod = _git_date(paths[0]) or TODAY
    state[loc] = {"sha256": digest, "lastmod": lastmod}
    _state_dirty = True
    return lastmod


def _save_state(locs: set[str]) -> None:
    state = _load_state()
    pruned = {loc: state[loc] for loc in sorted(state) if loc in locs}
    if _state_dirty or pruned != state:
        LASTMOD_STATE.write_text(json.dumps(pruned, indent=1, sort_keys=True) + "\n", encoding="utf-8")


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
            if not page.get("indexable", True):
                continue
            loc = page.get("canonical") or f"{BASE}/{page['path'].replace('.html', '')}"
            if loc in seen:
                continue
            add_url(urlset, loc, page.get("priority", "0.75"), "monthly")
            seen.add(loc)

    _save_state(seen)
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(SITEMAP, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote {len(seen)} URLs to {SITEMAP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
