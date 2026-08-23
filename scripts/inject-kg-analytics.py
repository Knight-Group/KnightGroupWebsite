#!/usr/bin/env python3
"""Insert the shared analytics loader and bump includes cache-busters."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_FILES = {"header.html", "footer.html", "socialCards.html"}
SKIP_DIR_NAMES = {"node_modules", "website-audit", "gsc-audit"}
ANALYTICS_SRC = "/JS/kg-analytics.js?v=20260823-analytics"
ANALYTICS_TAG = f'    <script src="{ANALYTICS_SRC}"></script>\n'
NOSCRIPT = (
    '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MNHVDBHG" '
    'height="0" width="0" style="display:none;visibility:hidden" '
    'title="Google Tag Manager"></iframe></noscript>\n'
)
INCLUDES_PAT = re.compile(r"/JS/includes\.min\.js\?v=[^\"']+")
INCLUDES_NEW = "/JS/includes.min.js?v=20260823-analytics"
HEAD_CLOSE = re.compile(r"</head>", re.IGNORECASE)
BODY_OPEN = re.compile(r"<body\b[^>]*>", re.IGNORECASE)


def should_skip(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return True
    if path.parent.name == "scripts" and path.name.startswith("legacy"):
        return True
    if path.parent.name == "scripts" and path.name.endswith("-legacy.html"):
        return True
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def inject_analytics(text: str) -> tuple[str, bool]:
    if ANALYTICS_SRC in text or "kg-analytics.js" in text:
        return text, False
    match = HEAD_CLOSE.search(text)
    if not match:
        return text, False
    return text[: match.start()] + ANALYTICS_TAG + text[match.start() :], True


def inject_noscript(text: str) -> tuple[str, bool]:
    if "googletagmanager.com/ns.html" in text:
        return text, False
    match = BODY_OPEN.search(text)
    if not match:
        return text, False
    insert_at = match.end()
    return text[:insert_at] + "\n" + NOSCRIPT + text[insert_at:], True


def main() -> int:
    analytics_added = 0
    noscript_added = 0
    includes_updated = 0
    missing_head = []

    for path in sorted(ROOT.rglob("*.html")):
        if should_skip(path):
            continue
        text = path.read_text(encoding="utf-8")
        original = text

        if not HEAD_CLOSE.search(text):
            missing_head.append(str(path.relative_to(ROOT)))

        text, added_analytics = inject_analytics(text)
        if added_analytics:
            analytics_added += 1

        text, added_noscript = inject_noscript(text)
        if added_noscript:
            noscript_added += 1

        new_text, n = INCLUDES_PAT.subn(INCLUDES_NEW, text)
        if n:
            includes_updated += 1
            text = new_text

        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")

    print(f"kg-analytics injected: {analytics_added}")
    print(f"GTM noscript injected: {noscript_added}")
    print(f"includes version bumped: {includes_updated}")
    if missing_head:
        print("pages without </head>:")
        for item in missing_head:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
