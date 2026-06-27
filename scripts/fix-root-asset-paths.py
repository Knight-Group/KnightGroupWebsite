#!/usr/bin/env python3
"""Normalize site asset URLs to root-relative /Images, /JS, /CSS, /GalleryImages paths."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOTS = ("Images", "JS", "CSS", "GalleryImages")
ATTR_RE = re.compile(
    r'(?P<attr>src|href|srcset|content)=(["\'])(?P<path>(?:\.\./)*(?:'
    + "|".join(ASSET_ROOTS)
    + r')/[^"\']*)(?P<q>\2)'
)


def to_root(path: str) -> str:
    base, sep, query = path.partition("?")
    base = base.lstrip("/")
    while base.startswith("../"):
        base = base[3:]
    normalized = f"/{base}"
    return f"{normalized}{sep}{query}" if sep else normalized


def fix_srcset(value: str) -> str:
    parts = []
    for chunk in value.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        tokens = piece.split()
        if not tokens:
            continue
        tokens[0] = to_root(tokens[0])
        parts.append(" ".join(tokens))
    return ", ".join(parts)


def fix_text(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        attr = match.group("attr")
        quote = match.group("q")
        path = match.group("path")
        fixed = fix_srcset(path) if attr == "srcset" and "," in path else to_root(path)
        return f'{attr}={quote}{fixed}{quote}'

    return ATTR_RE.sub(repl, text)


def fix_manifest(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for image in data.get("images", []):
        src = image.get("src")
        if isinstance(src, str) and not src.startswith("/"):
            image["src"] = to_root(src)
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    html_changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".venv", "node_modules", "scripts"} for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            html_changed += 1
            print(f"fixed {path.relative_to(ROOT)}")

    manifest = ROOT / "Images" / "hero-panels" / "manifest.json"
    if manifest.is_file() and fix_manifest(manifest):
        print("fixed Images/hero-panels/manifest.json")

    print(f"updated {html_changed} html file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
