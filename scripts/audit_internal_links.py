#!/usr/bin/env python3
"""Find orphan pages and pages with only one internal inbound link."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"scripts", "legacy", "admin", "node_modules", ".venv", "seo", "Chess-Game-main", "page-template.html"}


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def normalize_href(href: str) -> str | None:
    href = href.strip()
    if not href or href.startswith("#"):
        return None
    if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(href)
    path = parsed.path or href
    path = path.lstrip("/")
    if not path:
        return "index.html"
    if path.endswith("/"):
        path = path[:-1]
    if path.endswith(".html"):
        return path
    if "/" in path:
        return f"{path}.html"
    return f"{path}.html"


def main() -> int:
    pages: dict[str, set[str]] = {}
    for path in sorted(ROOT.rglob("*.html")):
        if is_skipped(path):
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        pages[rel] = set()

    link_re = re.compile(r"""<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']""", re.I)
    for path in sorted(ROOT.rglob("*.html")):
        if is_skipped(path):
            continue
        src = str(path.relative_to(ROOT)).replace("\\", "/")
        html = path.read_text(encoding="utf-8", errors="ignore")
        for href in link_re.findall(html):
            target = normalize_href(href)
            if target and target in pages:
                pages[target].add(src)

    indexable_orphans = [
        rel
        for rel, inbound in sorted(pages.items())
        if not inbound and not rel.startswith("PolicyPages/")
    ]
    single_link = sorted(
        [(rel, len(inbound)) for rel, inbound in pages.items() if len(inbound) == 1 and not rel.startswith("PolicyPages/")],
        key=lambda item: item[0],
    )

    print(f"Tracked HTML pages: {len(pages)}")
    print(f"Orphan indexable pages: {len(indexable_orphans)}")
    for rel in indexable_orphans:
        print(f"  ORPHAN {rel}")
    print(f"Single inbound link: {len(single_link)}")
    for rel, count in single_link:
        print(f"  SINGLE {count} {rel}")
    return 1 if indexable_orphans else 0


if __name__ == "__main__":
    raise SystemExit(main())
