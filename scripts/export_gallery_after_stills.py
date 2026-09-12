#!/usr/bin/env python3
"""Export one Dispatch after photo per gallery job as a related-card WebP still.

Related cards crop to ~400x300. A before/process/after composite reads as a
collage at that size. This writes GalleryImages/after-{slug}.webp from the
scope's after photos in Handyman Ticket Manager uploads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

from PIL import Image, ImageOps, ImageStat

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from service_related import after_still_web_path  # noqa: E402

HTM_ROOT = Path(os.environ.get("HTM_ROOT", r"E:\Handyman Ticket Manager"))
if str(HTM_ROOT) not in sys.path:
    sys.path.insert(0, str(HTM_ROOT))

from ticket_manager.photos import photo_file_path  # noqa: E402
from ticket_manager.state_paths import tickets_db_path  # noqa: E402

GALLERY_DIR = ROOT / "GalleryImages"
MANIFEST = GALLERY_DIR / "gallery-manifest.json"
HASH_RE = re.compile(r"-([0-9a-f]{7})(?:-before-after)?$")
CARD_SIZE = (800, 600)
HASH_SEED = "{ticket_number}:{scope_id}:{scope_slug}"

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass


def group_hash(group_id: str) -> str | None:
    match = HASH_RE.search(str(group_id).strip())
    return match.group(1) if match else None


def scope_hash(ticket_number: str, scope_id: int, scope_slug: str) -> str:
    seed = HASH_SEED.format(
        ticket_number=ticket_number,
        scope_id=scope_id,
        scope_slug=scope_slug or "",
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:7]


def taken_at(image: Image.Image) -> str:
    try:
        exif = image.getexif()
        return str(exif.get(36867) or exif.get(306) or "")
    except Exception:
        return ""


def _unique_colors(rgb: Image.Image) -> int:
    thumb = rgb.resize((48, 48), Image.Resampling.BILINEAR)
    raw = thumb.tobytes()
    return len(
        {
            (raw[i] >> 4, raw[i + 1] >> 4, raw[i + 2] >> 4)
            for i in range(0, len(raw), 3)
        }
    )


def _has_sky(rgb: Image.Image) -> bool:
    width, height = rgb.size
    top = rgb.crop((0, 0, width, max(1, height // 5))).resize((32, 8))
    red, green, blue = ImageStat.Stat(top).mean
    return blue > 140 and blue >= red - 10 and green > 120


def score_after(image: Image.Image) -> tuple[int, int, int, str]:
    rgb = ImageOps.exif_transpose(image).convert("RGB")
    width, height = rgb.size
    return (
        int(_has_sky(rgb)),
        int(width >= height),
        _unique_colors(rgb),
        taken_at(image),
    )


def crop_to_card(image: Image.Image, size: tuple[int, int] = CARD_SIZE) -> Image.Image:
    rgb = ImageOps.exif_transpose(image).convert("RGB")
    src_w, src_h = rgb.size
    target_w, target_h = size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = max(1, int(src_h * target_ratio))
        x = (src_w - new_w) // 2
        rgb = rgb.crop((x, 0, x + new_w, src_h))
    elif src_ratio < target_ratio:
        new_h = max(1, int(src_w / target_ratio))
        y = int((src_h - new_h) * 0.32)
        rgb = rgb.crop((0, y, src_w, y + new_h))
    return rgb.resize(size, Image.Resampling.LANCZOS)


def write_still(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        card = crop_to_card(image)
        card.save(dest, "WEBP", quality=80, method=6)


def load_groups() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [g for g in data.get("groups") or [] if str(g.get("id") or "").strip()]


def build_scope_index(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT ts.id AS scope_id, ts.ticket_number, ts.slug AS scope_slug
        FROM ticket_scopes ts
        """
    ).fetchall()
    index: dict[str, sqlite3.Row] = {}
    for row in rows:
        index[scope_hash(row["ticket_number"], row["scope_id"], row["scope_slug"] or "")] = row
    return index


def list_after_photos(conn: sqlite3.Connection, ticket_number: str, scope_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT stored_filename, original_name, is_primary, sort_order, id
        FROM ticket_photos
        WHERE ticket_number = ?
          AND scope_id = ?
          AND kind = 'after'
          AND COALESCE(media_type, 'image') = 'image'
        ORDER BY is_primary DESC, sort_order ASC, id ASC
        """,
        (ticket_number, scope_id),
    ).fetchall()


def pick_after_path(ticket_number: str, photos: list[sqlite3.Row]) -> Path | None:
    ranked: list[tuple[tuple, Path]] = []
    for photo in photos:
        try:
            path = photo_file_path(ticket_number, photo["stored_filename"])
        except (FileNotFoundError, ValueError):
            continue
        try:
            with Image.open(path) as image:
                image.load()
                ranked.append((score_after(image), path))
        except Exception:
            continue
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


def export_stills(*, force: bool = False) -> dict[str, int]:
    groups = load_groups()
    db_path = tickets_db_path()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    index = build_scope_index(conn)
    stats = {"wrote": 0, "skipped_exists": 0, "no_hash": 0, "no_scope": 0, "no_after": 0}
    try:
        for group in groups:
            gid = str(group["id"]).strip()
            suffix = group_hash(gid)
            dest = ROOT.joinpath(*after_still_web_path(gid).lstrip("/").split("/"))
            if not suffix:
                stats["no_hash"] += 1
                continue
            if dest.is_file() and not force:
                stats["skipped_exists"] += 1
                continue
            scope = index.get(suffix)
            if scope is None:
                stats["no_scope"] += 1
                print(f"skip {gid}: no matching Dispatch scope")
                continue
            photos = list_after_photos(conn, scope["ticket_number"], scope["scope_id"])
            source = pick_after_path(scope["ticket_number"], photos)
            if source is None:
                stats["no_after"] += 1
                print(f"skip {gid}: no readable after photo")
                continue
            write_still(source, dest)
            stats["wrote"] += 1
            print(f"wrote {dest.name} from {source.name}")
    finally:
        conn.close()
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Export gallery related-card after stills")
    parser.add_argument("--force", action="store_true", help="Overwrite existing after-*.webp files")
    args = parser.parse_args()
    stats = export_stills(force=args.force)
    print(
        "after stills: "
        f"wrote={stats['wrote']} exists={stats['skipped_exists']} "
        f"no_hash={stats['no_hash']} no_scope={stats['no_scope']} no_after={stats['no_after']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
