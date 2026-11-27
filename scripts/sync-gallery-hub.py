#!/usr/bin/env python3
"""Sync a deterministic, generator-owned index of all gallery/*.html pages into galleries.html.

Rules (per 2026-10-31-gallery-hub-linking-plan.md):
- Preserve the <!-- KGWG hand-added ... --> ... <!-- /KGWG hand-added --> block byte-for-byte.
- Write <!-- GALLERY-INDEX:BEGIN --> ... <!-- GALLERY-INDEX:END --> immediately after
  <!-- /KGWG hand-added -->, never inside it.
- Link every gallery/*.html page on disk that is not already statically linked elsewhere
  in galleries.html, so 0 gallery pages are orphaned.
- Ensure #gallery-lightbox-img has a valid 1x1 transparent data-URI src (prevents broken-img audit hits).
- Fully idempotent. Run with --check for CI / pre-push 0-orphan verification.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERIES_HTML = ROOT / "galleries.html"
GALLERY_DIR = ROOT / "gallery"
MANIFEST_JSON = ROOT / "GalleryImages" / "gallery-manifest.json"

BEGIN_MARKER = "<!-- GALLERY-INDEX:BEGIN -->"
END_MARKER = "<!-- GALLERY-INDEX:END -->"
KGWG_END_MARKER = "<!-- /KGWG hand-added -->"
TRANSPARENT_GIF = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

HREF_RE = re.compile(r'href=["\'](?:/?gallery/)([a-z0-9-]+?)(?:\.html)?["\']', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)


def load_manifest_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    if not MANIFEST_JSON.is_file():
        return titles
    try:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        for g in data.get("groups", []):
            gid = (g.get("id") or "").strip()
            title = (g.get("title") or "").strip()
            if gid and title:
                titles[gid] = title
    except Exception:
        pass
    return titles


def resolve_title(slug: str, manifest_titles: dict[str, str]) -> str:
    if slug in manifest_titles:
        return manifest_titles[slug]
    page = GALLERY_DIR / f"{slug}.html"
    if page.is_file():
        raw = page.read_text(encoding="utf-8", errors="ignore")
        m = TITLE_RE.search(raw)
        if m:
            t = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
            t = re.sub(r"\s*\|\s*Knight Group.*$", "", t, flags=re.I).strip()
            if t:
                return t
    clean = re.sub(r"-[0-9a-f]{7}-before-after$", "", slug)
    clean = re.sub(r"-before-after$", "", clean)
    return clean.replace("-", " ").strip().capitalize() + " — before & after"


def build_updated_html(original: str) -> tuple[str, int, int]:
    if KGWG_END_MARKER not in original:
        raise RuntimeError(f"Missing required marker {KGWG_END_MARKER!r} in galleries.html")

    # Strip existing generated block (if any) to find static links outside it
    block_re = re.compile(
        r"\n?[ \t]*" + re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER),
        re.S,
    )
    without_generated = block_re.sub("", original)
    static_linked = set(HREF_RE.findall(without_generated))

    disk_slugs = sorted(p.stem for p in GALLERY_DIR.glob("*.html"))
    to_add = [s for s in disk_slugs if s not in static_linked]
    manifest_titles = load_manifest_titles()

    lines = [f"                {BEGIN_MARKER}"]
    for slug in to_add:
        label = html.escape(resolve_title(slug, manifest_titles))
        lines.append(f'                <li><a href="/gallery/{slug}">{label}</a></li>')
    lines.append(f"                {END_MARKER}")
    generated_block = "\n" + "\n".join(lines)

    updated = without_generated.replace(
        KGWG_END_MARKER,
        KGWG_END_MARKER + generated_block,
        1,
    )

    # Fix empty-src lightbox img (prevents false broken-image finding on /galleries)
    updated = re.sub(
        r'<img\s+id="gallery-lightbox-img"\s+alt="([^"]*)">',
        f'<img id="gallery-lightbox-img" src="{TRANSPARENT_GIF}" alt="\\1">',
        updated,
        count=1,
    )
    return updated, len(disk_slugs), len(to_add)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync gallery hub static index into galleries.html")
    parser.add_argument("--check", action="store_true", help="Verify 0 orphans and up-to-date block without writing")
    args = parser.parse_args()

    original = GALLERIES_HTML.read_text(encoding="utf-8")
    updated, total_pages, generated_count = build_updated_html(original)

    final_linked = set(HREF_RE.findall(updated))
    disk_slugs = {p.stem for p in GALLERY_DIR.glob("*.html")}
    orphans = sorted(disk_slugs - final_linked)

    if args.check:
        if orphans:
            print(f"FAIL: {len(orphans)} gallery orphan(s) would remain: {orphans[:10]}")
            return 1
        if original != updated:
            print(f"FAIL: galleries.html is out of sync ({generated_count} links needed). Run: python scripts/sync-gallery-hub.py")
            return 1
        print(f"OK: galleries.html in sync — {total_pages}/{total_pages} gallery pages linked, 0 orphans.")
        return 0

    if original != updated:
        GALLERIES_HTML.write_text(updated, encoding="utf-8", newline="\n")
        print(f"Updated galleries.html: {total_pages} total gallery pages, {generated_count} in GALLERY-INDEX, {len(orphans)} orphans.")
    else:
        print(f"Unchanged galleries.html: {total_pages} total gallery pages, {generated_count} in GALLERY-INDEX, {len(orphans)} orphans.")
    return 1 if orphans else 0


if __name__ == "__main__":
    raise SystemExit(main())
