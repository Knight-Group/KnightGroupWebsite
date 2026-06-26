#!/usr/bin/env python3
"""URL-encode spaces in GalleryImages/Images asset paths inside HTML attributes."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", "node_modules", "scripts", "Chess-Game-main", "seo-audit"}
ATTR_RE = re.compile(
    r'(?P<attr>src|href|srcset)=(["\'])(?P<path>(?:/)?(?:GalleryImages|Images)/[^"\']*)(?P<q>\2)',
    re.I,
)


def encode_asset_path(path: str) -> str:
    if "?" in path:
        base, query = path.split("?", 1)
        return encode_asset_path(base) + "?" + query
    leading = "/" if path.startswith("/") else ""
    body = path.lstrip("/")
    if "/" not in body:
        return path
    folder, filename = body.split("/", 1)
    if "%" in filename:
        filename = unquote(filename)
    encoded = f"{folder}/{quote(filename)}"
    return leading + encoded


def fix_srcset(value: str) -> str:
    parts = []
    for chunk in value.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        tokens = piece.split()
        if not tokens:
            continue
        tokens[0] = encode_asset_path(tokens[0])
        parts.append(" ".join(tokens))
    return ", ".join(parts)


def fix_text(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        attr = match.group("attr")
        quote = match.group("q")
        path = match.group("path")
        fixed = fix_srcset(path) if attr.lower() == "srcset" and "," in path else encode_asset_path(path)
        return f"{attr}={quote}{fixed}{quote}"

    return ATTR_RE.sub(repl, text)


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"encoded asset paths in {path.relative_to(ROOT)}")
    print(f"updated {changed} html file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
