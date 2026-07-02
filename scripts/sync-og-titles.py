#!/usr/bin/env python3
"""Sync og:title and twitter:title with the document <title> on HTML pages."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"scripts", "legacy", "Chess-Game-main", "admin", "page-template.html"}

TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.I)
OG_TITLE_RE = re.compile(r'(<meta property="og:title" content=")([^"]*)(")', re.I)
TW_TITLE_RE = re.compile(r'(<meta name="twitter:title" content=")([^"]*)(")', re.I)


def esc(value: str) -> str:
    return html.escape(value.strip(), quote=True)


def replace_title_tag(match: re.Match[str], title: str) -> str:
    return match.group(1) + esc(title) + match.group(3)


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = TITLE_RE.search(text)
        if not match:
            continue
        title = match.group(1).strip()
        updated = text
        if OG_TITLE_RE.search(updated):
            updated = OG_TITLE_RE.sub(lambda m: replace_title_tag(m, title), updated, count=1)
        if TW_TITLE_RE.search(updated):
            updated = TW_TITLE_RE.sub(lambda m: replace_title_tag(m, title), updated, count=1)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"synced: {path.relative_to(ROOT)}")
    print(f"Done. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
