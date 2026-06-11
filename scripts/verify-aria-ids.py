#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    for ref in re.findall(r'aria-labelledby="([^"]+)"', text):
        for part in ref.split():
            if part and f'id="{part}"' not in text and f"id='{part}'" not in text:
                missing.append(part)
    return sorted(set(missing))


def main() -> int:
    paths = sorted(ROOT.glob("Services/*.html"))
    bad = False
    for path in paths:
        missing = check_file(path)
        if missing:
            bad = True
            print(f"{path.name}: MISSING {missing}")
        else:
            print(f"{path.name}: OK")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
