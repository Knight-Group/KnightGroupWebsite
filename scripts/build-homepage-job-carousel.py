#!/usr/bin/env python3
"""Build homepage recent-jobs carousel cards from gallery-manifest.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "GalleryImages" / "gallery-manifest.json"
INDEX_PATH = ROOT / "index.html"

# Prefer a specific frame when a group has many progression photos.
IMAGE_OVERRIDES = {
    "fixtures-fans-electrical": "fixtures-fans-02.webp",
    "bathroom-tub-window-remodel": "Refinishing_Bathroom_Window2.webp",
    "room-refinish": "Refinished_Room2.webp",
    "mold-wall-repair": "Moldy_Wall2.webp",
    "floor-subfloor-repair": "fixing_floor2.webp",
    "window-wall-repair": "Window_Wall2.webp",
    "tub-drain-replacement": "NewTubDrain.webp",
}

# Surface stronger before/after and finished shots near the front.
GROUP_ORDER = [
    "fridge-door-alignment-before-after",
    "pipe-repair-before-after",
    "tub-drain-before-after",
    "room-restoration-before-after",
    "stove-burner-repair-before-after",
    "blinds-replacement-before-after",
    "hornet-removal-wall-sealed-before-after",
    "bathroom-tub-window-remodel",
    "bathroom-remodel-cobblestone",
    "garbage-disposal-install",
    "tub-drain-replacement",
    "floor-subfloor-repair",
    "mold-wall-repair",
    "window-wall-repair",
    "hvac-vent-boxing",
    "room-refinish",
    "fixtures-fans-electrical",
]


def pick_image(group: dict) -> dict | None:
    images = group.get("images") or []
    if not images:
        return None

    override = IMAGE_OVERRIDES.get(group["id"])
    if override:
        for image in images:
            if image.get("filename") == override:
                return image

    before_after = [image for image in images if image.get("beforeAfter")]
    if before_after:
        return before_after[0]

    if group.get("progression"):
        return max(images, key=lambda image: image.get("step", 0))

    return images[0]


def gallery_src(filename: str) -> str:
    return f"/GalleryImages/{quote(filename)}"


def image_exists(filename: str) -> bool:
    path = ROOT / "GalleryImages" / filename
    return path.is_file() and path.stat().st_size >= 512


def render_card(group: dict, image: dict) -> str:
    filename = image["filename"]
    src = gallery_src(filename)
    alt = html.escape(image.get("seoAlt") or group["title"], quote=True)
    title = html.escape(group["title"], quote=False)
    description = html.escape(group["description"], quote=False)
    return (
        f'<article class="kg-job-card"><picture>'
        f'<source srcset="{src}" type="image/webp">'
        f'<img src="{src}" alt="{alt}" loading="eager" decoding="async" width="640" height="480" data-kg-static="true">'
        f"</picture><div><h3>{title}</h3><p>{description}</p></div></article>"
    )


def build_cards() -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    groups_by_id = {group["id"]: group for group in manifest.get("groups", [])}

    ordered_ids = [group_id for group_id in GROUP_ORDER if group_id in groups_by_id]
    for group_id in groups_by_id:
        if group_id not in ordered_ids:
            ordered_ids.append(group_id)

    cards: list[str] = []
    for group_id in ordered_ids:
        group = groups_by_id[group_id]
        image = pick_image(group)
        if not image:
            continue
        filename = image.get("filename", "")
        if not filename or not image_exists(filename):
            continue
        cards.append(render_card(group, image))

    return "\n                            ".join(cards)


def patch_index(cards_html: str) -> None:
    index_html = INDEX_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<div class="kg-job-track" id="kg-job-track">\s*)(.*?)(\s*</div>\s*</div>\s*<button class="kg-job-btn" type="button" id="kg-job-next")',
        re.DOTALL,
    )
    match = pattern.search(index_html)
    if not match:
        raise RuntimeError("Could not find kg-job-track block in index.html")

    updated = pattern.sub(
        rf"\1\n                            {cards_html}\n                        \3",
        index_html,
        count=1,
    )
    INDEX_PATH.write_text(updated, encoding="utf-8")


def main() -> int:
    cards_html = build_cards()
    card_count = cards_html.count('class="kg-job-card"')
    if card_count < 8:
        raise RuntimeError(f"Expected at least 8 carousel cards, got {card_count}")
    patch_index(cards_html)
    import subprocess
    import sys

    subprocess.run([sys.executable, str(ROOT / "scripts" / "verify-homepage-carousel.py")], check=True)
    print(f"Wrote {card_count} homepage job carousel cards to {INDEX_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
