#!/usr/bin/env python3
"""Audit geo page image references on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    broken: list[tuple[str, str]] = []
    patterns = list(ROOT.glob("*-handyman.html"))
    patterns += [
        p
        for p in ROOT.glob("*.html")
        if re.search(
            r"-(sink-repair|drywall-repair|home-repair|toilet-repair|door-adjustment|trim-repair|interior-painting)\.html$",
            p.name,
        )
    ]

    for html in patterns:
        text = html.read_text(encoding="utf-8")
        for match in re.finditer(r'src="([^"]+)"', text):
            src = match.group(1).split("?")[0]
            if not (
                src.startswith("Images/")
                or src.startswith("GalleryImages/")
                or "/GalleryImages/" in src
                or "/Images/" in src
            ):
                continue
            rel = src.lstrip("/").replace("../", "")
            path = ROOT / rel.replace("/", "\\")
            if not path.is_file():
                broken.append((html.name, src))

    print(f"checked {len(patterns)} geo pages")
    print(f"broken: {len(broken)}")
    for page, src in sorted(broken):
        print(f"  {page} -> {src}")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
