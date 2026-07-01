#!/usr/bin/env python3
"""Generate responsive WebP variants for homepage performance (card + carousel sizes)."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CARD_WIDTH = 400
CAROUSEL_WIDTH = 640
HERO_CUTOUT_WIDTHS = (400, 680, 960)

SERVICE_WEBPS = [
    "general-repairs",
    "plumbing-services",
    "electrical-work",
    "carpentry-framing",
    "painting-finishing",
    "home-renovations",
    "doors-windows",
    "custom-projects",
    "emergency-services",
    "handyman",
]

CUSTOM_CARD_WEBPS = [
    "kg-leaky-pipes.webp",
    "KG-fixture.webp",
    "kg-door-window-repair.webp",
    "kg-waterheater-pipe-burst.webp",
]

CAROUSEL_GALLERY = [
    "before-after-fridge-wouldnt-close-does-now.webp",
    "KnightGroupBeforeAfterPipes.webp",
    "KnightGroup_before_after_drain.webp",
    "KnightGroup_before_after_room.webp",
    "before-after-broken-stove-burner-fixed.webp",
    "before-after-broken-blinds-replaced.webp",
    "before-after-horney-removal-wall-sealed.webp",
    "Refinished Bathroom_Window.webp",
    "Refinished_Bathroom.webp",
    "GarbageDisposal.webp",
    "NewTubDrain.webp",
    "fixing_floor2.webp",
    "Moldy_Wall2.webp",
    "Window_Wall2.webp",
    "AC_Vent_Box.webp",
    "Refinished_Room2.webp",
    "fixtures-fans-02.webp",
]


def save_webp(src: Path, dest: Path, width: int, quality: int = 78) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.width <= width:
            if dest == src or dest.resolve() == src.resolve():
                return False
            img.save(dest, "WEBP", quality=quality, method=6)
            return True
        ratio = width / img.width
        height = max(1, round(img.height * ratio))
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(dest, "WEBP", quality=quality, method=6)
    return True


def variant_path(src: Path, width: int) -> Path:
    return src.with_name(f"{src.stem}-{width}w{src.suffix}")


def main() -> int:
    created = 0
    services_dir = ROOT / "Images" / "services"
    for slug in SERVICE_WEBPS:
        src = services_dir / f"{slug}.webp"
        dest = variant_path(src, CARD_WIDTH)
        if save_webp(src, dest, CARD_WIDTH):
            created += 1
            print(f"card: {dest.relative_to(ROOT)}")

    for name in CUSTOM_CARD_WEBPS:
        src = ROOT / "Images" / name
        dest = variant_path(src, CARD_WIDTH)
        if save_webp(src, dest, CARD_WIDTH):
            created += 1
            print(f"card: {dest.relative_to(ROOT)}")

    gallery_dir = ROOT / "GalleryImages"
    for name in CAROUSEL_GALLERY:
        src = gallery_dir / name
        dest = variant_path(src, CAROUSEL_WIDTH)
        if save_webp(src, dest, CAROUSEL_WIDTH):
            created += 1
            print(f"carousel: {dest.relative_to(ROOT)}")

    cutout = ROOT / "Images" / "knight-hero-cutout.webp"
    for width in HERO_CUTOUT_WIDTHS:
        dest = variant_path(cutout, width)
        if save_webp(cutout, dest, width, quality=82):
            created += 1
            print(f"hero: {dest.relative_to(ROOT)}")

    hero_panels = ROOT / "Images" / "hero-panels"
    for src in sorted(hero_panels.glob("*.webp")):
        if re.search(r"-\d+w\.webp$", src.name, re.I):
            continue
        dest = variant_path(src, 720)
        if save_webp(src, dest, 720, quality=80):
            created += 1
            print(f"panel: {dest.relative_to(ROOT)}")

    print(f"Done. {created} variants written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
