#!/usr/bin/env python3
"""Legacy entrypoint retained for compatibility; delegates to the scope guard."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"legacy", "__pycache__", "scripts", "LICENSE.txt"}

REPLACEMENTS = [
    ("licensed &amp; insured", "registered and insured"),
    ("licensed & insured", "registered and insured"),
    ("Licensed, insured, and local to Safety Harbor", "Registered, insured, and local to Safety Harbor"),
    (
        "Is Knight Group licensed and insured in Florida?",
        "Is Knight Group registered and insured in Florida?",
    ),
    (
        "Yes. Knight Group Handyman Services LLC is registered and fully insured in Florida, giving homeowners, landlords, and property managers peace of mind on every job.",
        "Yes. Knight Group Handyman Services LLC is a registered and insured handyman business in Florida. We handle handyman-scope repairs, fixture-level plumbing repairs, and minor electrical fixture support within our current service scope, and we refer licensed professionals when required.",
    ),
]

BANNED_SELF_LICENSE = re.compile(
    r"(?<!refer )(?<!requires a )(?<!need a )(?<!licensed )"
    r"\b(licensed &amp; insured|licensed & insured|Licensed, insured)\b",
    re.I,
)


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        text = original
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"updated {path.relative_to(ROOT)}")
    print(f"fixed licensed wording on {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
