#!/usr/bin/env python3
"""List HTML img tags missing meaningful alt text."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"legacy", "__pycache__", "scripts"}


def main() -> int:
    issues: list[tuple[str, int, str]] = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_no, line in enumerate(lines, start=1):
            for tag in re.findall(r"<img\b[^>]*>", line, flags=re.I):
                alt_match = re.search(r'\balt\s*=\s*(["\'])(.*?)\1', tag, flags=re.I)
                if not alt_match or not alt_match.group(2).strip():
                    issues.append((path.relative_to(ROOT).as_posix(), line_no, tag[:140]))

    print(f"{len(issues)} img tags missing alt text")
    for rel, line_no, tag in issues:
        print(f"{rel}:{line_no}: {tag}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
