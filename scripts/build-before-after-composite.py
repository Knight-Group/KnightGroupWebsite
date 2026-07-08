#!/usr/bin/env python3
"""Build branded before / process / after collage matching the stove template design.

Dynamic layout:
  - 2–8 images total, any mix of before / repair-process / after buckets
  - Process column appears only when repair-process* files exist
  - Each column stacks or grids its images; photos use fit-contain (full image visible)

Filename convention:
  before-<slug>.*           -> before column
  fixed-<slug>.* / after-* -> after column
  repair-process*          -> process column (repair-process, repair-process1, …)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "GalleryImages" / "before-after-broken-stove-burner-fixed.webp"
ASSETS_DIR = ROOT / "scripts" / "composite-assets"
LOGO_PATH = ROOT / "Images" / "KnightGroupLogo.png"
DEFAULT_OUT = ROOT / "GalleryImages"

TEMPLATE_SIZE = (1672, 941)
LOGO_BOX = (28, 10, 228, 208)
TITLE_MASK = (200, 18, 1470, 198)
TITLE_MAX_WIDTH = TITLE_MASK[2] - TITLE_MASK[0] - 56
TITLE_FONT_SIZES = (98, 88, 78, 68, 58, 50, 42, 36)
TITLE_LINE_GAP = 8
FOOTER_Y = 750

GALLERY_BOTTOM = 748
GALLERY_LEFT = 12
GALLERY_RIGHT = 1660
LABEL_Y = 208
LABEL_FONT_SIZE = 38
LABEL_GAP_BELOW = 4

MARGIN_X = 12
COL_GAP = 18
SLOT_GAP = 8
CELL_PAD = 2

WHITE = (255, 255, 255)
RED = (194, 28, 28)
BLACK = (0, 0, 0)
CELL_BG = (12, 12, 12)

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

LABEL_FILES = {
    "before": "label-before.png",
    "process": "label-process.png",
    "after": "label-after.png",
}

LABEL_TEXT = {
    "before": "BEFORE",
    "process": "REPAIR PROCESS",
    "after": "AFTER",
}

SPLATTER_POS = (1380, 0)
# Header ends ~y200 (title + splatter); section labels sit just below that band
HEADER_BOTTOM = 204

@dataclass
class ColumnLayout:
    key: str
    x0: int
    x1: int
    images: list[Path] = field(default_factory=list)
    slots: list[tuple[int, int, int, int]] = field(default_factory=list)


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
        if re.fullmatch(r"[0-9a-f]{32}", name):
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


def load_photo(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


def fit_contain(im: Image.Image, w: int, h: int, *, bg: tuple[int, int, int] = CELL_BG) -> Image.Image:
    im = im.convert("RGB")
    src_w, src_h = im.size
    if src_w < 1 or src_h < 1:
        return Image.new("RGB", (w, h), bg)
    scale = min(w / src_w, h / src_h)
    nw, nh = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    out = Image.new("RGB", (w, h), bg)
    out.paste(resized, ((w - nw) // 2, (h - nh) // 2))
    return out


def allocate_slots(x0: int, y0: int, x1: int, y1: int, count: int) -> list[tuple[int, int, int, int]]:
    """Divide a column into photo cells — side-by-side for 2 portraits in wide columns."""
    if count <= 0:
        return []
    ix0, iy0, ix1, iy1 = x0 + CELL_PAD, y0 + CELL_PAD, x1 - CELL_PAD, y1 - CELL_PAD
    iw, ih = ix1 - ix0, iy1 - iy0
    if count == 1:
        return [(ix0, iy0, ix1, iy1)]

    gap = SLOT_GAP

    if count == 2:
        if iw >= ih * 1.15:
            w_each = (iw - gap) // 2
            return [
                (ix0, iy0, ix0 + w_each, iy1),
                (ix0 + w_each + gap, iy0, ix1, iy1),
            ]
        h_each = (ih - gap) // 2
        return [
            (ix0, iy0, ix1, iy0 + h_each),
            (ix0, iy0 + h_each + gap, ix1, iy1),
        ]

    if count == 3:
        if iw >= ih * 1.15:
            w_each = (iw - gap) // 2
            h_each = (ih - gap) // 2
            return [
                (ix0, iy0, ix0 + w_each, iy0 + h_each),
                (ix0 + w_each + gap, iy0, ix1, iy0 + h_each),
                (ix0, iy0 + h_each + gap, ix1, iy1),
            ]
        h_each = (ih - gap * 2) // 3
        slots = []
        y = iy0
        for _ in range(3):
            slots.append((ix0, y, ix1, y + h_each))
            y += h_each + gap
        return slots

    cols = 2
    rows = (count + cols - 1) // cols
    gap_x, gap_y = SLOT_GAP, SLOT_GAP
    cell_w = (iw - gap_x * (cols - 1)) // cols
    cell_h = (ih - gap_y * (rows - 1)) // rows
    slots: list[tuple[int, int, int, int]] = []
    for i in range(count):
        row, col = divmod(i, cols)
        sx = ix0 + col * (cell_w + gap_x)
        sy = iy0 + row * (cell_h + gap_y)
        slots.append((sx, sy, sx + cell_w, sy + cell_h))
    return slots


def plan_columns(buckets: dict[str, list[Path]]) -> list[ColumnLayout]:
    active: list[tuple[str, list[Path]]] = []
    if buckets["before"]:
        active.append(("before", buckets["before"]))
    if buckets["process"]:
        active.append(("process", buckets["process"]))
    if buckets["after"]:
        active.append(("after", buckets["after"]))

    if not active:
        raise ValueError("No before/after/process photos found")

    n = len(active)
    total_w = GALLERY_RIGHT - GALLERY_LEFT
    gaps = COL_GAP * (n - 1)
    col_w = (total_w - gaps) // n

    columns: list[ColumnLayout] = []
    x = GALLERY_LEFT
    for key, images in active:
        columns.append(ColumnLayout(key=key, x0=x, x1=x + col_w, images=images))
        x += col_w + COL_GAP
    return columns


def assign_photo_slots(columns: list[ColumnLayout], gallery_top: int) -> None:
    for col in columns:
        col.slots = allocate_slots(col.x0, gallery_top, col.x1, GALLERY_BOTTOM, len(col.images))


def split_title(title: str) -> tuple[str, str]:
    title = " ".join(title.upper().split())
    if " & " in title:
        left, right = title.split(" & ", 1)
        return left.strip(), f"& {right.strip()}"
    words = title.split()
    if len(words) >= 2:
        mid = len(words) // 2
        return " ".join(words[:mid]), " ".join(words[mid:])
    return title, ""


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _pick_headline_layout(
    draw: ImageDraw.ImageDraw,
    white_part: str,
    red_part: str,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, bool]:
    """Pick font size; use two stacked lines when the headline is long."""
    combined_len = len(f"{white_part} {red_part}".strip() if red_part else white_part)
    prefer_two_lines = combined_len > 40

    for size in TITLE_FONT_SIZES:
        font = load_font(size, bold=True, italic=True)
        if red_part and prefer_two_lines:
            if max(_text_width(draw, white_part, font), _text_width(draw, red_part, font)) <= TITLE_MAX_WIDTH:
                return font, True
        elif red_part:
            total = _text_width(draw, white_part + " ", font) + _text_width(draw, red_part, font)
            if total <= TITLE_MAX_WIDTH:
                return font, False
        elif _text_width(draw, white_part, font) <= TITLE_MAX_WIDTH:
            return font, False

    font = load_font(TITLE_FONT_SIZES[-1], bold=True, italic=True)
    if red_part:
        if max(_text_width(draw, white_part, font), _text_width(draw, red_part, font)) <= TITLE_MAX_WIDTH:
            return font, prefer_two_lines
        return font, True
    return font, _text_width(draw, white_part, font) > TITLE_MAX_WIDTH


def draw_headline(canvas: Image.Image, title: str) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(TITLE_MASK, fill=BLACK)
    white_part, red_part = split_title(title)
    cx = (TITLE_MASK[0] + TITLE_MASK[2]) // 2
    center_y = TITLE_MASK[1] + (TITLE_MASK[3] - TITLE_MASK[1]) // 2

    font, two_lines = _pick_headline_layout(draw, white_part, red_part)

    if two_lines and red_part:
        w_bbox = draw.textbbox((0, 0), white_part, font=font)
        r_bbox = draw.textbbox((0, 0), red_part, font=font)
        lh = max(w_bbox[3] - w_bbox[1], r_bbox[3] - r_bbox[1])
        total_h = lh * 2 + TITLE_LINE_GAP
        y_white = center_y - total_h // 2
        y_red = y_white + lh + TITLE_LINE_GAP
        tw = w_bbox[2] - w_bbox[0]
        draw.text((cx - tw // 2, y_white), white_part, fill=WHITE, font=font)
        rw = r_bbox[2] - r_bbox[0]
        draw.text((cx - rw // 2, y_red), red_part, fill=RED, font=font)
    elif two_lines and not red_part:
        words = white_part.split()
        mid = max(1, len(words) // 2)
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        b1 = draw.textbbox((0, 0), line1, font=font)
        b2 = draw.textbbox((0, 0), line2, font=font)
        lh = max(b1[3] - b1[1], b2[3] - b2[1])
        total_h = lh * 2 + TITLE_LINE_GAP
        y1 = center_y - total_h // 2
        y2 = y1 + lh + TITLE_LINE_GAP
        w1 = b1[2] - b1[0]
        w2 = b2[2] - b2[0]
        draw.text((cx - w1 // 2, y1), line1, fill=WHITE, font=font)
        draw.text((cx - w2 // 2, y2), line2, fill=WHITE, font=font)
    elif red_part:
        w_bbox = draw.textbbox((0, 0), white_part + " ", font=font)
        r_bbox = draw.textbbox((0, 0), red_part, font=font)
        total_w = (w_bbox[2] - w_bbox[0]) + (r_bbox[2] - r_bbox[0])
        cy = center_y - (w_bbox[3] - w_bbox[1]) // 2
        x = cx - total_w // 2
        draw.text((x, cy), white_part + " ", fill=WHITE, font=font)
        draw.text((x + w_bbox[2] - w_bbox[0], cy), red_part, fill=RED, font=font)
    else:
        bbox = draw.textbbox((0, 0), white_part, font=font)
        cy = center_y - (bbox[3] - bbox[1]) // 2
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


def load_clean_label(key: str) -> Image.Image:
    """Load brush label PNG without trimming the top (only trim photo bleed below the banner)."""
    path = ASSETS_DIR / LABEL_FILES[key]
    if not path.is_file():
        raise FileNotFoundError(f"Missing label asset: {path}")
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    last_red = 0
    for y in range(h):
        reds = sum(1 for x in range(w) if im.getpixel((x, y))[0] > 120 and im.getpixel((x, y))[3] > 80)
        if reds > 8:
            last_red = y
    return im.crop((0, 0, w, last_red + 1))


def draw_brush_label(canvas: Image.Image, text: str, *, center_x: int, y: int) -> int:
    """Draw a red section label with full text visible; return y below the banner."""
    draw = ImageDraw.Draw(canvas)
    font = load_font(LABEL_FONT_SIZE, bold=True, italic=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 34, 10
    bar_h = th + pad_y * 2
    bar_w = tw + pad_x * 2
    x0 = center_x - bar_w // 2

    draw.rectangle((x0, y, x0 + bar_w, y + bar_h), fill=RED)
    tx = center_x - tw // 2 - bbox[0]
    ty = y + (bar_h - th) // 2 - bbox[1]
    draw.text((tx, ty), text, fill=WHITE, font=font)
    return y + bar_h


def paste_splatter(canvas: Image.Image) -> None:
    path = ASSETS_DIR / "splatter.png"
    if not path.is_file():
        return
    splatter = Image.open(path).convert("RGBA")
    canvas.paste(splatter, SPLATTER_POS, splatter)


def restore_footer(canvas: Image.Image, template: Image.Image) -> None:
    w, h = canvas.size
    canvas.paste(template.crop((0, FOOTER_Y, w, h)), (0, FOOTER_Y))


def paste_photo_contain(canvas: Image.Image, slot: tuple[int, int, int, int], path: Path) -> None:
    x0, y0, x1, y1 = slot
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    photo = fit_contain(load_photo(path), w, h)
    canvas.paste(photo, (x0, y0))


def infer_title(buckets: dict[str, list[Path]], explicit: str | None) -> str:
    if explicit:
        return explicit.upper()
    for path in buckets["before"] + buckets["after"] + buckets["process"]:
        stem = path.stem.lower()
        if stem.startswith("before-"):
            return stem.removeprefix("before-").replace("-", " ").upper()
        if stem.startswith("fixed-"):
            return stem.removeprefix("fixed-").replace("-", " ").upper()
        if stem.startswith("after-"):
            return stem.removeprefix("after-").replace("-", " ").upper()
        if stem.startswith("repair-process"):
            slug = stem.removeprefix("repair-process").lstrip("0123456789-")
            if slug:
                return slug.replace("-", " ").upper()
    return "HANDYMAN REPAIR"


def layout_summary(columns: list[ColumnLayout]) -> str:
    parts = [f"{c.key}x{len(c.images)}" for c in columns]
    return " + ".join(parts)


def build_composite(*, buckets: dict[str, list[Path]], title: str) -> Image.Image:
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"Reference template missing: {TEMPLATE_PATH}")

    template = Image.open(TEMPLATE_PATH).convert("RGB")
    if template.size != TEMPLATE_SIZE:
        template = template.resize(TEMPLATE_SIZE, Image.Resampling.LANCZOS)

    # Fresh black canvas — never copy template photos into the gallery zone
    canvas = Image.new("RGB", TEMPLATE_SIZE, BLACK)
    paste_splatter(canvas)
    paste_logo(canvas)
    draw_headline(canvas, title)

    # Clear band between headline and gallery so nothing overlaps section labels
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, HEADER_BOTTOM, TEMPLATE_SIZE[0], FOOTER_Y), fill=BLACK)

    columns = plan_columns(buckets)
    label_bottom = LABEL_Y
    for col in columns:
        cx = (col.x0 + col.x1) // 2
        label_bottom = max(
            label_bottom,
            draw_brush_label(canvas, LABEL_TEXT[col.key], center_x=cx, y=LABEL_Y),
        )

    gallery_top = label_bottom + LABEL_GAP_BELOW
    assign_photo_slots(columns, gallery_top)

    for col in columns:
        for slot, path in zip(col.slots, col.images):
            paste_photo_contain(canvas, slot, path)

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
    total = sum(len(v) for v in buckets.values())
    if total < 2:
        raise SystemExit(f"Need at least 2 photos; found {total}")

    title = infer_title(buckets, args.title)
    base = args.basename or f"before-after-{title.lower().replace(' ', '-')}"
    base = re.sub(r"[^\w\-]+", "-", base).strip("-").lower()

    columns = plan_columns(buckets)
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

    print(f"\nLayout: {layout_summary(columns)} ({total} images)")
    for col in columns:
        for path in col.images:
            print(f"  {col.key.upper():8} {path.name}")

    if args.publish:
        publish = ROOT / "scripts" / "publish-before-after-gallery.py"
        cmd = [sys.executable, str(publish), "--basename", base]
        if args.deploy:
            cmd.append("--deploy")
        subprocess.run(cmd, cwd=str(ROOT), check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
