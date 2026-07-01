#!/usr/bin/env python3
"""Scan repo for common mojibake / encoding defects."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"node_modules", ".git", "__pycache__", "screenshots"}

BAD_FRAGMENTS = [
    "â€",
    "ï¿½",
    "\ufffd",
    "colorado-.",
    "Quality home .",
    "Memphis, TN",
    "warranty responsibility ?",
]

SKIP_SCAN_PREFIXES = ("seo-audit/", "scripts/legacy-")
SKIP_SCAN_FILES = {
    "seo/serp-meta-research.json",
    "seo/serp-meta-research.md",
    "seo/meta-descriptions.json",
}


def main() -> int:
    hits: list[tuple[str, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel in SKIP_SCAN_FILES:
            continue
        if rel.startswith(SKIP_SCAN_PREFIXES):
            continue
        if path.suffix not in {".html", ".txt"}:
            continue
        if any(part in SKIP for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for frag in BAD_FRAGMENTS:
            if frag in text:
                hits.append((str(path.relative_to(ROOT)), frag))
                break
    print(f"Found {len(hits)} files with encoding/meta defects:")
    for rel, frag in sorted(hits):
        print(f"  {rel}  ({frag!r})")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
