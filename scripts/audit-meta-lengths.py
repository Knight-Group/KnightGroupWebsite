#!/usr/bin/env python3
"""Audit title and meta description lengths across HTML pages."""

from __future__ import annotations

from html import unescape
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"scripts", "legacy", "Chess-Game-main", "admin", "node_modules"}
SKIP_FILES = {
    "page-template.html",
    "404.html",
    "footer.html",
    "header.html",
    "head-gtm.html",
    "socialCards.html",
    "index.html",
    "handcraftedfurniture&resins.html",
    "programming&databases.html",
}
TITLE_MAX = 60
DESC_MIN = 120
DESC_MAX = 159
BAD_DESC_PATTERNS = [
    re.compile(r"Memphis,\s*TN", re.I),
    re.compile(r"colorado-", re.I),
    re.compile(r"Quality home\s*\.", re.I),
    re.compile(r"in Clear\.", re.I),
    re.compile(r"â€", re.I),
    re.compile(r"ï¿½"),
    re.compile(r"\ufffd"),
]


def main() -> int:
    title_long: list[tuple[str, int]] = []
    desc_short: list[tuple[str, int]] = []
    desc_long: list[tuple[str, int]] = []
    desc_bad: list[tuple[str, str]] = []
    missing_desc: list[str] = []

    for path in sorted(ROOT.rglob("*.html")):
        if path.name in SKIP_FILES or any(part in SKIP_PARTS for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(ROOT))

        title_match = re.search(r"<title>([^<]+)</title>", content, re.I)
        if title_match:
            title = unescape(title_match.group(1).strip())
            if len(title) > TITLE_MAX:
                title_long.append((rel, len(title)))

        desc_match = re.search(r'<meta name="description" content="([^"]*)"', content, re.I)
        if not desc_match:
            missing_desc.append(rel)
            continue
        desc = desc_match.group(1)
        desc_len = len(desc)
        if desc_len < DESC_MIN:
            desc_short.append((rel, desc_len))
        if desc_len > DESC_MAX:
            desc_long.append((rel, desc_len))
        for pattern in BAD_DESC_PATTERNS:
            if pattern.search(desc):
                desc_bad.append((rel, pattern.pattern))
                break

    issues = len(title_long) + len(desc_short) + len(desc_long) + len(missing_desc) + len(desc_bad)
    print(f"title > {TITLE_MAX}: {len(title_long)}")
    for rel, n in title_long[:15]:
        print(f"  {n:3d} {rel}")
    print(f"description missing: {len(missing_desc)}")
    for rel in missing_desc[:15]:
        print(f"  {rel}")
    print(f"description < {DESC_MIN}: {len(desc_short)}")
    for rel, n in desc_short[:15]:
        print(f"  {n:3d} {rel}")
    print(f"description > {DESC_MAX}: {len(desc_long)}")
    for rel, n in desc_long[:15]:
        print(f"  {n:3d} {rel}")
    print(f"description quality defects: {len(desc_bad)}")
    for rel, pat in desc_bad[:15]:
        print(f"  {rel}  ({pat})")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
