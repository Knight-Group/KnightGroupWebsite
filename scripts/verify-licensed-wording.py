#!/usr/bin/env python3
"""Fail if risky self-licensing wording appears in public site HTML."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"legacy", "__pycache__", "scripts"}

BANNED = [
    re.compile(r"licensed\s*&\s*insured", re.I),
    re.compile(r"Licensed,\s*insured", re.I),
    re.compile(r"Is Knight Group licensed and insured", re.I),
]


def main() -> int:
    failures: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT).as_posix()
        for pattern in BANNED:
            if pattern.search(text):
                failures.append(f"{rel}: {pattern.pattern}")
    if failures:
        print("Licensed wording verification failed:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("Licensed wording verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
