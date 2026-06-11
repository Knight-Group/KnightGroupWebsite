#!/usr/bin/env python3
"""Verify Knight Group NAP consistency across site source files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAP = json.loads((ROOT / "seo" / "knight-group-nap.json").read_text(encoding="utf-8"))

SCAN_GLOBS = ("*.html", "*.json", "*.js", "*.txt", "*.md", "*.css", "*.xml")
SKIP_PARTS = {"__pycache__", "seo-audit", "gsc-export", "node_modules"}
SKIP_PREFIXES = ("legacy-", "lighthouse-run")


def iter_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        for path in ROOT.rglob(pattern):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if any(path.name.startswith(prefix) for prefix in SKIP_PREFIXES):
                continue
            if path.suffix == ".json" and path.stat().st_size > 2_000_000:
                continue
            files.append(path)
    return sorted(set(files))


def main() -> int:
    failures: list[str] = []
    deprecated_patterns = [
        re.compile(r"727[\s.\-]?215[\s.\-]?7685", re.I),
        re.compile(r"\+1[\s.\-]?727[\s.\-]?215[\s.\-]?7685", re.I),
    ]

    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT).as_posix()
        if rel == "seo/knight-group-nap.json":
            continue
        for pattern in deprecated_patterns:
            if pattern.search(text):
                failures.append(f"{rel}: deprecated phone number found")
        if "+1-813-649-3341" in text:
            failures.append(f"{rel}: non-canonical schema telephone format (+1-813-649-3341)")

    required_present = {
        "phoneDisplay": NAP["phoneDisplay"],
        "email": NAP["email"],
        "website": NAP["website"],
    }
    for check_file in ("footer.html", "llms.txt", "contact.html"):
        path = ROOT / check_file
        if not path.exists():
            failures.append(f"{check_file}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for label, value in required_present.items():
            if value not in text:
                failures.append(f"{check_file}: missing canonical {label} ({value})")

    if failures:
        print("NAP verification failed:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("NAP verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
