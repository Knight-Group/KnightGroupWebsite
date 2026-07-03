#!/usr/bin/env python3
"""Publish a before/after composite to website gallery + Google Drive (social JPG).

Expects in GalleryImages/:
  {basename}.webp
  {basename}-640w.webp
  {basename}-social.jpg

Run after build-before-after-composite.py --also-jpeg.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "GalleryImages"
SMM_ROOT = Path(r"E:\KnightLogics-Growth-System\Social\Social-Media-Manager")
DRIVE_UPLOAD = SMM_ROOT / "scheduled_brand_posting" / "drive" / "upload_to_gallery.py"
BUILD_MANIFEST = ROOT / "scripts" / "build-gallery-manifest.py"
BUILD_CAROUSEL = ROOT / "scripts" / "build-homepage-job-carousel.py"
BUILD_SEO = ROOT / "scripts" / "build-seo-pages.py"
BUILD_SCHEMA = ROOT / "scripts" / "build-schema-graph.py"
BUILD_SITEMAP = ROOT / "scripts" / "build-sitemap.py"
OPTIMIZE_IMAGES = ROOT / "scripts" / "optimize-home-images.py"
KG_MEDIA_LIB = SMM_ROOT / "scheduled_brand_posting" / "media_library" / "kg"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd or ROOT), check=True)


def webp_basename(basename: str) -> str:
    return basename if basename.endswith(".webp") else f"{basename}.webp"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish before/after gallery composite")
    parser.add_argument(
        "--basename",
        required=True,
        help="Base name without extension, e.g. before-after-ac-vent-filter-change",
    )
    parser.add_argument("--skip-drive", action="store_true", help="Skip Google Drive upload")
    parser.add_argument("--deploy", action="store_true", help="Git commit and push to origin/main")
    parser.add_argument(
        "--commit-message",
        default="",
        help="Git commit message (default: auto from basename)",
    )
    args = parser.parse_args()

    base = re.sub(r"[^\w\-]+", "-", args.basename.strip()).strip("-").lower()
    webp = GALLERY_DIR / webp_basename(base)
    social = GALLERY_DIR / f"{base}-social.jpg"
    webp_640 = GALLERY_DIR / f"{base}-640w.webp"

    missing = [p for p in (webp, social) if not p.is_file()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(str(p) for p in missing)}")

    run([sys.executable, str(BUILD_MANIFEST)])

    manifest = json.loads((GALLERY_DIR / "gallery-manifest.json").read_text(encoding="utf-8"))
    groups = {g["id"]: g for g in manifest.get("groups", [])}
    catalog_name = webp.name
    group_id = None
    for g in groups.values():
        for img in g.get("images", []):
            if img.get("filename") == catalog_name:
                group_id = g["id"]
                break
    if not group_id:
        raise SystemExit(
            f"{catalog_name} not in gallery-manifest.json — add IMAGE_CATALOG entry in "
            "build-gallery-manifest.py first, then re-run."
        )

    alt = ""
    for img in manifest.get("images", []):
        if img.get("filename") == catalog_name:
            alt = img.get("seoAlt") or img.get("title") or ""
            break

    if not args.skip_drive:
        if not DRIVE_UPLOAD.is_file():
            raise SystemExit(f"Drive upload script missing: {DRIVE_UPLOAD}")
        try:
            run(
                [
                    sys.executable,
                    str(DRIVE_UPLOAD),
                    str(social),
                    "--brand",
                    "kg",
                    "--description",
                    alt[:500],
                ]
            )
        except subprocess.CalledProcessError:
            print(
                "WARNING: Google Drive upload failed (browser auth may be required). "
                "Re-run upload_to_gallery.py manually, or use --skip-drive.",
                file=sys.stderr,
            )

    KG_MEDIA_LIB.mkdir(parents=True, exist_ok=True)
    dest = KG_MEDIA_LIB / social.name
    shutil.copy2(social, dest)
    print(f"Copied social JPG → {dest}")

    if not webp_640.is_file():
        run([sys.executable, str(OPTIMIZE_IMAGES)])
    run([sys.executable, str(BUILD_CAROUSEL)])
    run([sys.executable, str(BUILD_SEO)])
    run([sys.executable, str(BUILD_SCHEMA)])
    run([sys.executable, str(BUILD_SITEMAP)])

    if args.deploy:
        msg = args.commit_message or f"Add gallery before/after: {group_id}"
        paths = [
            str(webp.relative_to(ROOT)),
            str(webp_640.relative_to(ROOT)) if webp_640.is_file() else "",
            str(social.relative_to(ROOT)),
            "GalleryImages/gallery-manifest.json",
            f"gallery/{group_id}.html",
            "galleries.html",
            "index.html",
            "sitemap.xml",
            "seo/page-manifest.json",
            "scripts/build-gallery-manifest.py",
            "scripts/build-homepage-job-carousel.py",
            "scripts/build-before-after-composite.py",
            "scripts/publish-before-after-gallery.py",
            "scripts/gallery_detail_copy.py",
            "scripts/build-seo-pages.py",
            "scripts/serp_query_map.py",
            "scripts/optimize-home-images.py",
        ]
        paths = [p for p in paths if p]
        run(["git", "add", *paths], cwd=ROOT)
        run(["git", "status", "-sb"], cwd=ROOT)
        run(["git", "commit", "-m", msg], cwd=ROOT)
        run(["git", "push", "origin", "main"], cwd=ROOT)
        print("Deployed to origin/main")

    print(f"\nPublished {base}")
    print(f"  Gallery group: {group_id}")
    print(f"  Live URL: https://www.knightgroup.com/gallery/{group_id}")
    print(f"  Social JPG: {social}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
