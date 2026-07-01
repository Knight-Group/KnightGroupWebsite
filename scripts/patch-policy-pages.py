#!/usr/bin/env python3
"""Align policy pages with site-wide header/footer includes and dark theme."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = ROOT / "PolicyPages"
INCLUDE_VERSION = "20260701-unified-includes"
ASSET_VERSION = "20260701-unified-includes"

HEAD_ASSETS = f"""
    <link rel="stylesheet" href="/CSS/header.min.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/CSS/kg-redesign.css?v={ASSET_VERSION}">
    <script src="/JS/kg-redesign.js?v={ASSET_VERSION}" defer></script>
""".strip()

POLICY_INLINE_STYLE = (
    "<style>"
    ".kg-policy-page .page-hero{color:#fff;padding:clamp(72px,10vw,100px) 0;text-align:center}"
    ".kg-policy-page .page-hero h1{font-family:'Playfair Display',Georgia,serif;font-size:clamp(2rem,4vw,3rem);margin-bottom:16px}"
    ".kg-policy-page .page-hero p{font-size:1.15rem;opacity:.9;max-width:640px;margin:0 auto}"
    ".kg-policy-stack{padding:0 0 clamp(56px,7vw,84px)}"
    "@media (max-width:768px){.kg-policy-page .policy-content,.kg-policy-page .terms-content{margin:0 16px;padding:32px 22px}}"
    "</style>"
)

HEADER_PATTERN = re.compile(
    r'<div id="header-include">.*?</div>\s*(?=<main id="main-content">)',
    re.DOTALL,
)

INLINE_POLICY_STYLE = re.compile(
    r"<style>\*?\{margin:0;padding:0;box-sizing:border-box\}body\{[^<]*policy-content[^<]*</style>",
    re.DOTALL,
)
INLINE_TERMS_STYLE = re.compile(
    r"<style>\*?\{margin:0;padding:0;box-sizing:border-box\}body\{[^<]*terms-content[^<]*</style>",
    re.DOTALL,
)
INLINE_RETURN_STYLE = re.compile(
    r"<style>\*?\{margin:0;padding:0;box-sizing:border-box\}body\{[^<]*return-content[^<]*</style>",
    re.DOTALL,
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = HEADER_PATTERN.sub('<div id="header-include"></div>\n\n    ', text)

    if '<body class="kg-page kg-policy-page">' not in text:
        text = text.replace("<body>", '<body class="kg-page kg-policy-page">', 1)

    if "header.min.css" not in text:
        text = text.replace("</head>", f"{HEAD_ASSETS}\n</head>", 1)

    for pattern in (INLINE_POLICY_STYLE, INLINE_TERMS_STYLE, INLINE_RETURN_STYLE):
        if pattern.search(text):
            text = pattern.sub(POLICY_INLINE_STYLE, text, count=1)
            break

    if 'class="kg-policy-stack"' not in text:
        text = text.replace(
            '<main id="main-content">',
            '<main id="main-content">\n    <div class="kg-policy-stack">',
            1,
        )
        text = text.replace(
            "\n    </main>",
            "\n    </div>\n    </main>",
            1,
        )

    text = re.sub(
        r'<script src="/JS/includes\.min\.js\?v=[^"]+" defer></script>',
        f'<script src="/JS/includes.min.js?v={INCLUDE_VERSION}" defer></script>',
        text,
        count=1,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for path in sorted(POLICY_DIR.glob("*.html")):
        if patch_file(path):
            print(f"patched {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} policy page(s) updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
