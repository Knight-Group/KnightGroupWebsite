#!/usr/bin/env python3
"""Sync meta description + og:description + twitter:description from seo/meta-descriptions.json."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "seo" / "meta-descriptions.json"
SKIP_PARTS = {"scripts", "legacy", "Chess-Game-main", "admin", "node_modules"}
SKIP_FILES = {"page-template.html", "404.html", "footer.html", "header.html", "head-gtm.html", "socialCards.html"}

sys.path.insert(0, str(ROOT / "scripts"))
from page_meta import clip_meta  # noqa: E402

DESC_RE = re.compile(r'(<meta name="description" content=")([^"]*)(")', re.I)
OG_DESC_RE = re.compile(r'(<meta property="og:description" content=")([^"]*)(")', re.I)
TW_DESC_RE = re.compile(r'(<meta name="twitter:description" content=")([^"]*)(")', re.I)


def esc(value: str) -> str:
    return html.escape(value.strip(), quote=True)


def apply_description(text: str, description: str) -> str:
    updated = text
    if DESC_RE.search(updated):
        updated = DESC_RE.sub(rf"\1{esc(description)}\3", updated, count=1)
    if OG_DESC_RE.search(updated):
        updated = OG_DESC_RE.sub(rf"\1{esc(description)}\3", updated, count=1)
    if TW_DESC_RE.search(updated):
        updated = TW_DESC_RE.sub(rf"\1{esc(description)}\3", updated, count=1)
    return updated


def main() -> int:
    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    desc_map = {
        str(entry["path"]).replace("\\", "/"): clip_meta(str(entry["description"]))
        for entry in data.get("pages", [])
        if entry.get("path") and entry.get("description")
    }

    changed = 0
    for rel, description in sorted(desc_map.items()):
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = apply_description(text, description)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"synced: {rel} ({len(description)} chars)")

    print(f"Done. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
