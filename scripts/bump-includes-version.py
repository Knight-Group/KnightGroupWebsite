#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = re.compile(r"/JS/includes\.min\.js\?v=[^\"']+")
NEW = "/JS/includes.min.js?v=20260701-unified-includes"


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        if path.parts[-2:] == ("scripts", path.name) and path.name.startswith("legacy"):
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = PAT.subn(NEW, text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"updated includes version in {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
