#!/usr/bin/env python3
"""Restructure service-page layout so the sidebar stays sticky through FAQ/related sections."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACK_MARK = "kg-service-main"
SECTION_RE = re.compile(
    r'<section class="kg-section kg-service-(?:faq|related|cta)"[\s\S]*?</section>',
    re.DOTALL,
)


def extract_div_block(html: str, class_name: str, start_at: int = 0) -> tuple[str, int, int] | None:
    token = f'<div class="{class_name}">'
    open_idx = html.find(token, start_at)
    if open_idx == -1:
        return None
    cursor = open_idx + len(token)
    depth = 1
    while cursor < len(html) and depth > 0:
        next_open = html.find("<div", cursor)
        next_close = html.find("</div>", cursor)
        if next_close == -1:
            return None
        if next_open != -1 and next_open < next_close:
            depth += 1
            cursor = next_open + 4
            continue
        depth -= 1
        cursor = next_close + len("</div>")
        if depth == 0:
            return html[open_idx + len(token) : next_close], open_idx, cursor
    return None


def strip_shell(section_html: str) -> str:
    section_html = re.sub(
        r'(<section class="kg-section kg-service-(?:faq|related|cta)"[^>]*>)\s*<div class="kg-shell">\s*',
        r"\1\n                    ",
        section_html,
        count=1,
    )
    section_html = re.sub(
        r"\n\s*</div>\s*(</section>)",
        r"\n            \1",
        section_html,
        count=1,
    )
    return section_html


def patch_html(html: str) -> tuple[str, bool]:
    if STACK_MARK in html:
        return html, False

    stack_idx = html.find('<div class="kg-service-stack">')
    if stack_idx == -1:
        return html, False

    detail_open = html.find('<section class="kg-section kg-service-detail"', stack_idx)
    if detail_open == -1:
        return html, False

    detail_tag_end = html.find(">", detail_open) + 1
    prose_block = extract_div_block(html, "kg-service-prose", detail_open)
    if not prose_block:
        return html, False
    prose_inner, _, prose_close = prose_block

    sidebar_match = re.search(
        r"<aside class=\"kg-service-sidebar\"[\s\S]*?</aside>",
        html[prose_close:],
    )
    if not sidebar_match:
        return html, False
    sidebar_html = sidebar_match.group(0).strip()
    sidebar_close = prose_close + sidebar_match.end()

    detail_close = html.find("</section>", sidebar_close) + len("</section>")
    stack_end = html.find("\n        </div>\n    </main>", stack_idx)
    if stack_end == -1:
        return html, False

    middle = html[detail_close:stack_end]
    tail_start = stack_end + len("\n        </div>")
    sections = [strip_shell(block.strip()) for block in SECTION_RE.findall(middle)]
    if not sections:
        return html, False

    detail_attrs = html[detail_open + len('<section class="kg-section kg-service-detail"') : detail_tag_end - 1]

    rebuilt = f"""        <div class="kg-service-stack">
            <div class="kg-shell kg-service-layout">
                <div class="kg-service-main">
            <section class="kg-section kg-service-detail"{detail_attrs}>
                        <div class="kg-service-prose">
{prose_inner.strip()}
                        </div>
            </section>
{chr(10).join(sections)}
                </div>

                        {sidebar_html}
            </div>
        </div>"""

    new_html = html[:stack_idx] + rebuilt + html[tail_start:]
    return new_html, True


def iter_targets() -> list[Path]:
    paths: set[Path] = set()
    paths.update((ROOT / "Services").glob("*.html"))
    paths.update((ROOT / "gallery").glob("*.html"))
    paths.update(ROOT.glob("*-handyman.html"))
    paths.update(ROOT.glob("pricing-*.html"))
    paths.update(ROOT.glob("*-drywall-repair.html"))
    paths.update(ROOT.glob("*-home-repair.html"))
    paths.update(ROOT.glob("*-sink-repair.html"))
    paths.update(ROOT.glob("*-toilet-repair.html"))
    paths.update(ROOT.glob("*-interior-painting.html"))
    paths.update(ROOT.glob("*-door-adjustment.html"))
    return sorted(paths)


def main() -> int:
    changed = 0
    for path in iter_targets():
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "kg-service-stack" not in text:
            continue
        patched, ok = patch_html(text)
        if not ok:
            continue
        path.write_text(patched, encoding="utf-8")
        changed += 1
        print(f"patched: {path.relative_to(ROOT)}")

    print(f"Done. {changed} files restructured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
