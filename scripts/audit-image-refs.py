#!/usr/bin/env python3
"""Audit image src references across HTML against files on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".venv", "node_modules", "scripts", "Chess-Game-main", "seo-audit"}
ATTR_RE = re.compile(r'(?:src|href|srcset)=["\']([^"\']+)["\']', re.I)


def local_path(url: str) -> Path | None:
    url = unquote(url.split("?", 1)[0].strip())
    if not url or url.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
        return None
    if url.startswith("/"):
        rel = url.lstrip("/")
    elif re.match(r"^(Images|GalleryImages|CSS|JS)/", url):
        rel = url
    else:
        return None
    if not rel.startswith(("Images/", "GalleryImages/", "CSS/", "JS/")):
        return None
    return ROOT / rel


def audit_file(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for match in ATTR_RE.finditer(text):
        raw = match.group(1)
        for piece in raw.split(","):
            candidate = piece.strip().split()[0] if piece.strip() else ""
            local = local_path(candidate)
            if not local:
                continue
            if not local.is_file():
                issues.append((candidate, "missing"))
            elif local.stat().st_size < 512:
                issues.append((candidate, f"tiny ({local.stat().st_size} bytes)"))
    return issues


def main() -> int:
    all_issues: dict[str, list[str]] = {}
    for html in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_PARTS for part in html.parts):
            continue
        issues = audit_file(html)
        if issues:
            all_issues[str(html.relative_to(ROOT))] = [f"{url} -> {reason}" for url, reason in issues]

    if not all_issues:
        print("All local asset references resolve to non-empty files.")
        return 0

    total = sum(len(v) for v in all_issues.values())
    print(f"Found {total} broken asset reference(s) in {len(all_issues)} file(s):")
    for file_path, items in all_issues.items():
        print(f"\n{file_path}")
        for item in items:
            print(f"  - {item}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
