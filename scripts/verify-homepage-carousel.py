#!/usr/bin/env python3
"""Verify homepage job carousel image files exist."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    match = re.search(
        r'id="kg-job-track"[^>]*>(.*?)</div>\s*</div>\s*<button class="kg-job-btn" type="button" id="kg-job-next"',
        text,
        re.DOTALL,
    )
    if not match:
        print("kg-job-track not found")
        return 1

    srcs = re.findall(r'src="([^"]+)"', match.group(1))
    bad = []
    for src in srcs:
        path = ROOT / unquote(src.lstrip("/").split("?", 1)[0])
        if not path.is_file() or path.stat().st_size < 512:
            bad.append((src, "missing" if not path.is_file() else f"{path.stat().st_size} bytes"))

    print(f"carousel images: {len(srcs)}")
    if bad:
        for src, reason in bad:
            print(f"BAD {src} ({reason})")
        return 1
    print("all carousel image files ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
