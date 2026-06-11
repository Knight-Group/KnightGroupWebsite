#!/usr/bin/env python3
"""Apply GSC-driven meta descriptions and matching og:description tags."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "seo" / "meta-descriptions.json"
SERP_PATH = ROOT / "seo" / "serp-meta-research.json"
MAX_LEN = 159
PRIMARY_WINDOW = 80

META_RE = re.compile(
    r'(<meta name="description" content=")([^"]*)(")',
    re.I,
)
OG_RE = re.compile(
    r'(<meta property="og:description" content=")([^"]*)(")',
    re.I,
)
TWITTER_RE = re.compile(
    r'(<meta name="twitter:description" content=")([^"]*)(")',
    re.I,
)


def escape_attr(value: str) -> str:
    return html.escape(value, quote=True).replace("&#x27;", "'")


def validate(description: str, path: str) -> list[str]:
    issues: list[str] = []
    if len(description) > MAX_LEN:
        issues.append(f"{path}: {len(description)} chars (max {MAX_LEN})")
    if len(description) < 70:
        issues.append(f"{path}: description may be too short ({len(description)} chars)")
    primary = description[:PRIMARY_WINDOW].lower()
    if not any(
        token in primary
        for token in (
            "pinellas",
            "safety harbor",
            "knight group",
            "clearwater",
            "policy",
            "handyman",
        )
    ):
        issues.append(f"{path}: primary service/city missing in first {PRIMARY_WINDOW} chars")
    return issues


def apply_description(html_text: str, description: str) -> str:
    escaped = escape_attr(description)
    updated = META_RE.sub(rf"\1{escaped}\3", html_text, count=1)
    if OG_RE.search(updated):
        updated = OG_RE.sub(rf"\1{escaped}\3", updated, count=1)
    if TWITTER_RE.search(updated):
        updated = TWITTER_RE.sub(rf"\1{escaped}\3", updated, count=1)
    return updated


def main() -> int:
    if not SERP_PATH.exists():
        print(f"Missing Serper research: {SERP_PATH.relative_to(ROOT)}")
        print("Run: python scripts/serp-meta-research.py")
        return 1

    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    serper_at = data.get("serper_generated_at")
    if not serper_at:
        print("meta-descriptions.json is missing serper_generated_at. Run Serper research first.")
        return 1

    failures: list[str] = []
    changed = 0

    for entry in data["pages"]:
        rel_path = entry["path"]
        description = entry["description"].strip()
        path = ROOT / rel_path
        failures.extend(validate(description, rel_path))
        if not path.exists():
            failures.append(f"{rel_path}: file missing")
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_description(original, description)
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8")
        changed += 1
        print(f"updated: {rel_path} ({len(description)} chars)")

    if failures:
        print("\nValidation issues:")
        for issue in failures:
            print(f"  - {issue}")
        return 1

    print(f"\nDone. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
