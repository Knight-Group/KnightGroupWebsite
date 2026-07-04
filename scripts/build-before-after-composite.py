#!/usr/bin/env python3
"""Build branded before / process / after collage matching the stove template design.

Uses GalleryImages/before-after-broken-stove-burner-fixed.webp as layout chrome
(labels, arrows, footer, splatter, subtitle bar) and replaces logo, headline, and photos.

Filename convention:
  before-<slug>.*          -> left panel
  fixed-<slug>.* / after-* -> right panel
  repair-process.*         -> center top
  repair-process1.*        -> center bottom
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "GalleryImages" / "before-after-broken-stove-burner-fixed.webp"
ASSETS_DIR = ROOT / "scripts" / "composite-assets"
LOGO_PATH = ROOT / "Images" / "KnightGroupLogo.png"
DEFAULT_OUT = ROOT / "GalleryImages"

# Measured from 1672×941 master template
TEMPLATE_SIZE = (1672, 941)
LOGO_BOX = (28, 10, 228, 208)
# Main headline only — keep subtitle (y~200) and brush labels (y~248+) intact
TITLE_MASK = (200, 18, 1470, 198)

# Tilted template photos bleed above the white frames — wipe up to just below labels
BLEED_WIPE = {
    "before": (0, 276, 562, 362),
    "process": (557, 276, 1122, 362),
    "after": (1115, 276, 1672, 362),
}

# Inner photo paste areas — stop above footer chrome (branding starts ~y773)
INNER_BEFORE = (11, 369, 551, 738)
INNER_PROCESS_TOP = (568, 308, 1111, 487)
INNER_PROCESS_BOTTOM = (568, 504, 1111, 738)
INNER_AFTER = (1128, 308, 1650, 738)

# Black out any photo bleed, then re-paste template footer from this row down
FOOTER_Y = 750
COLUMN_BOTTOM_WIPE = (
    (0, 738, 562, FOOTER_Y),
    (557, 738, 1122, FOOTER_Y),
    (1115, 738, 1672, FOOTER_Y),
)

# Red brush labels (re-pasted above photos after swap)
LABEL_POS = {
    "before": (76, 238),
    "process": (601, 238),
    "after": (1161, 238),
}

WHITE = (255, 255, 255)
RED = (194, 28, 28)
BLACK = (0, 0, 0)

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def load_font(size: int, *, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if bold and italic:
        names = ["C:/Windows/Fonts/arialbi.ttf", "C:/Windows/Fonts/segoeuiz.ttf"]
    elif bold:
        names = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
    elif italic:
        names = ["C:/Windows/Fonts/ariali.ttf"]
    else:
        names = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for path in names:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def classify_photos(folder: Path) -> dict[str, list[Path]]:
    buckets: dict[str, list[Path]] = {"before": [], "after": [], "process": []}
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in PHOTO_EXTS:
            continue
        name = path.stem.lower()
        if name.startswith("before-after-"):
            continue
        if name.startswith("before-"):
            buckets["before"].append(path)
        elif name.startswith("fixed-") or name.startswith("after-"):
            buckets["after"].append(path)
        elif re.fullmatch(r"repair-process\d*", name):
            buckets["process"].append(path)
    buckets["process"].sort(
        key=lambda p: (0 if p.stem.lower() == "repair-process" else 1, p.stem.lower())
    )
    return buckets


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    src_w, src_h = im.size
    scale = max(w / src_w, h / src_h)
    nw, nh = int(src_w * scale), int(src_h * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def paste_photo(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    inner: tuple[int, int, int, int],
    path: Path | None,
) -> None:
    """Replace photo pixels only — keep template tilted white borders intact."""
    x0, y0, x1, y1 = inner
    inner_w, inner_h = x1 - x0, y1 - y0
    if inner_w < 8 or inner_h < 8:
        return
    draw.rectangle(inner, fill=BLACK)
    if not path:
        return
    photo = fit_cover(Image.open(path), inner_w, inner_h)
    canvas.paste(photo, (x0, y0))


def restore_footer(canvas: Image.Image, template: Image.Image) -> None:
    w, h = canvas.size
    strip = template.crop((0, FOOTER_Y, w, h))
    canvas.paste(strip, (0, FOOTER_Y))


def split_title(title: str) -> tuple[str, str]:
    """Split headline into white + red segments like BURNER / REPAIR."""
    title = " ".join(title.upper().split())
    if " & " in title:
        left, right = title.split(" & ", 1)
        return left.strip(), f"& {right.strip()}"
    words = title.split()
    if len(words) >= 2:
        mid = len(words) // 2
        return " ".join(words[:mid]), " ".join(words[mid:])
    return title, ""


def draw_headline(canvas: Image.Image, title: str) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(TITLE_MASK, fill=BLACK)
    white_part, red_part = split_title(title)
    font = load_font(98, bold=True, italic=True)
    cx = (TITLE_MASK[0] + TITLE_MASK[2]) // 2
    cy = TITLE_MASK[1] + 38

    if red_part:
        w_bbox = draw.textbbox((0, 0), white_part + " ", font=font)
        r_bbox = draw.textbbox((0, 0), red_part, font=font)
        total_w = (w_bbox[2] - w_bbox[0]) + (r_bbox[2] - r_bbox[0])
        x = cx - total_w // 2
        draw.text((x, cy), white_part + " ", fill=WHITE, font=font)
        draw.text((x + w_bbox[2] - w_bbox[0], cy), red_part, fill=RED, font=font)
    else:
        bbox = draw.textbbox((0, 0), white_part, font=font)
        draw.text((cx - (bbox[2] - bbox[0]) // 2, cy), white_part, fill=WHITE, font=font)


def paste_logo(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(LOGO_BOX, fill=BLACK)
    if not LOGO_PATH.is_file():
        return
    logo = Image.open(LOGO_PATH).convert("RGBA")
    x0, y0, x1, y1 = LOGO_BOX
    max_w, max_h = x1 - x0 - 6, y1 - y0 - 6
    lw, lh = logo.size
    scale = min(max_w / lw, max_h / lh)
    nw, nh = int(lw * scale), int(lh * scale)
    logo = logo.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = x0 + (max_w - nw) // 2 + 3
    oy = y0 + (max_h - nh) // 2 + 3
    canvas.paste(logo, (ox, oy), logo)


def infer_title(buckets: dict[str, list[Path]], explicit: str | None) -> str:
    if explicit:
        return explicit.upper()
    for path in buckets["before"] + buckets["after"]:
        stem = path.stem.lower()
        if stem.startswith("before-"):
            return stem.removeprefix("before-").replace("-", " ").upper()
        if stem.startswith("fixed-"):
            return stem.removeprefix("fixed-").replace("-", " ").upper()
        if stem.startswith("after-"):
            return stem.removeprefix("after-").replace("-", " ").upper()
    return "HANDYMAN REPAIR"


def paste_overlay(canvas: Image.Image, asset_name: str, xy: tuple[int, int]) -> None:
    path = ASSETS_DIR / f"{asset_name}.png"
    if not path.is_file():
        return
    overlay = Image.open(path).convert("RGBA")
    canvas.paste(overlay, xy, overlay)


def build_composite(*, buckets: dict[str, list[Path]], title: str) -> Image.Image:
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"Reference template missing: {TEMPLATE_PATH}")

    template = Image.open(TEMPLATE_PATH).convert("RGB")
    canvas = template.copy()
    if canvas.size != TEMPLATE_SIZE:
        template = template.resize(TEMPLATE_SIZE, Image.Resampling.LANCZOS)
        canvas = template.copy()

    paste_logo(canvas)
    draw_headline(canvas, title)

    draw = ImageDraw.Draw(canvas)
    for box in BLEED_WIPE.values():
        draw.rectangle(box, fill=BLACK)

    before = buckets["before"][0] if buckets["before"] else None
    after = buckets["after"][0] if buckets["after"] else None
    process = buckets["process"]

    paste_photo(draw, canvas, INNER_BEFORE, before)

    if len(process) >= 2:
        paste_photo(draw, canvas, INNER_PROCESS_TOP, process[0])
        paste_photo(draw, canvas, INNER_PROCESS_BOTTOM, process[1])
    elif len(process) == 1:
        merged_inner = (
            INNER_PROCESS_TOP[0],
            INNER_PROCESS_TOP[1],
            INNER_PROCESS_BOTTOM[2],
            INNER_PROCESS_BOTTOM[3],
        )
        paste_photo(draw, canvas, merged_inner, process[0])
    else:
        paste_photo(draw, canvas, INNER_PROCESS_TOP, None)
        paste_photo(draw, canvas, INNER_PROCESS_BOTTOM, None)

    paste_photo(draw, canvas, INNER_AFTER, after)

    for box in COLUMN_BOTTOM_WIPE:
        draw.rectangle(box, fill=BLACK)

    for key in ("before", "process", "after"):
        paste_overlay(canvas, f"label-{key}", LABEL_POS[key])

    restore_footer(canvas, template)

    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Knight Group before/after composite from renamed ticket photos.")
    parser.add_argument("folder", type=Path, help="Folder with before-*, fixed-*, repair-process* images")
    parser.add_argument("--title", help="Headline (default: inferred from filenames)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--basename", help="Output base name without extension")
    parser.add_argument("--also-jpeg", action="store_true")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="After build: upload social JPG to Drive + update website gallery (see publish-before-after-gallery.py)",
    )
    parser.add_argument("--deploy", action="store_true", help="With --publish: git commit and push")
    args = parser.parse_args()

    folder = args.folder.resolve()
    if not folder.is_dir():
        raise SystemExit(f"Not a folder: {folder}")

    buckets = classify_photos(folder)
    title = infer_title(buckets, args.title)
    base = args.basename or f"before-after-{title.lower().replace(' ', '-')}"
    base = re.sub(r"[^\w\-]+", "-", base).strip("-").lower()

    img = build_composite(buckets=buckets, title=title)
    args.out.mkdir(parents=True, exist_ok=True)

    full = args.out / f"{base}.webp"
    img.save(full, "WEBP", quality=90, method=6)
    print(f"Wrote {full} ({img.size[0]}x{img.size[1]})")

    small = args.out / f"{base}-640w.webp"
    img.resize((640, 360), Image.Resampling.LANCZOS).save(small, "WEBP", quality=88, method=6)
    print(f"Wrote {small}")

    if args.also_jpeg:
        jpg = args.out / f"{base}-social.jpg"
        img.save(jpg, "JPEG", quality=93, optimize=True, progressive=True)
        print(f"Wrote {jpg}")

    print("\nDetected files:")
    for key, label in [("before", "BEFORE"), ("process", "PROCESS"), ("after", "AFTER")]:
        for p in buckets[key]:
            print(f"  {label:8} {p.name}")

    if args.publish:
        publish = ROOT / "scripts" / "publish-before-after-gallery.py"
        cmd = [sys.executable, str(publish), "--basename", base]
        if args.deploy:
            cmd.append("--deploy")
        subprocess.run(cmd, cwd=str(ROOT), check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
