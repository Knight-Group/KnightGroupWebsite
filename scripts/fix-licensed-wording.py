#!/usr/bin/env python3
"""Replace risky self-licensing wording with registered-and-insured language."""

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
    changed_files = 0
    targets = sorted(ROOT.rglob("*.html"))
    targets += [ROOT / "llms.txt", ROOT / "seo" / "service-catalog.json"]
    for path in targets:
        if not path.is_file():
            continue
        if any(part in SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = text
        for old, new in REPLACEMENTS:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            print(f"updated: {path.relative_to(ROOT)}")
    print(f"Done. {changed_files} files updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
