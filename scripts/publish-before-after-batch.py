#!/usr/bin/env python3
"""Rebuild gallery site assets after adding IMAGE_CATALOG entries (no per-item deploy)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMM_ROOT = Path(r"E:\KnightLogics-Growth-System\Social\Social-Media-Manager")
DRIVE_UPLOAD = SMM_ROOT / "scheduled_brand_posting" / "drive" / "upload_to_gallery.py"
KG_MEDIA_LIB = SMM_ROOT / "scheduled_brand_posting" / "media_library" / "kg"
GALLERY_DIR = ROOT / "GalleryImages"

SCRIPTS = [
    "build-gallery-manifest.py",
    "optimize-home-images.py",
    "build-homepage-job-carousel.py",
    "build-seo-pages.py",
    "build-schema-graph.py",
    "build-sitemap.py",
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-drive", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--commit-message", default="Add before/after gallery batch")
    args = parser.parse_args()

    for name in SCRIPTS:
        run([sys.executable, str(ROOT / "scripts" / name)])

    social_files = sorted(GALLERY_DIR.glob("before-after-*-social.jpg"))
    KG_MEDIA_LIB.mkdir(parents=True, exist_ok=True)
    for src in social_files:
        dest = KG_MEDIA_LIB / src.name
        if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
            import shutil

            shutil.copy2(src, dest)
            print(f"Copied {src.name} -> media_library/kg/")

    if not args.skip_drive and DRIVE_UPLOAD.is_file():
        for src in social_files:
            try:
                run(
                    [
                        sys.executable,
                        str(DRIVE_UPLOAD),
                        str(src),
                        "--brand",
                        "kg",
                        "--description",
                        src.stem.replace("-social", "").replace("-", " ")[:500],
                    ]
                )
            except subprocess.CalledProcessError:
                print(f"WARNING: Drive upload failed for {src.name}", file=sys.stderr)

    if args.deploy:
        paths = [
            "GalleryImages/gallery-manifest.json",
            "galleries.html",
            "index.html",
            "sitemap.xml",
            "seo/page-manifest.json",
            "scripts/build-gallery-manifest.py",
            "scripts/gallery_detail_copy.py",
            "scripts/build-homepage-job-carousel.py",
            "scripts/build-seo-pages.py",
            "scripts/serp_query_map.py",
            "scripts/optimize-home-images.py",
            "scripts/publish-before-after-batch.py",
        ]
        for webp in sorted(GALLERY_DIR.glob("before-after-*.webp")):
            if "-640w" in webp.name or "-social" in webp.name:
                continue
            paths.append(str(webp.relative_to(ROOT)))
            w640 = GALLERY_DIR / f"{webp.stem}-640w.webp"
            if w640.is_file():
                paths.append(str(w640.relative_to(ROOT)))
        for social in social_files:
            paths.append(str(social.relative_to(ROOT)))
        for slug in sorted({p.parent.name for p in (ROOT / "gallery").glob("*")}):
            pass
        for html in sorted((ROOT / "gallery").glob("*.html")):
            if html.stem.startswith(
                (
                    "door-lock",
                    "curtain-rod",
                    "stair-tape",
                    "smoke-alarm",
                    "filter-change",
                    "carpet-removal",
                    "fire-extinguisher",
                    "blind-repair",
                    "kitchen-sink",
                    "door-wedge",
                )
            ) or html.stem.endswith("-before-after"):
                paths.append(str(html.relative_to(ROOT)))

        paths = sorted(set(paths))
        run(["git", "add", *paths])
        run(["git", "status", "-sb"])
        run(["git", "commit", "-m", args.commit_message])
        run(["git", "push", "origin", "main"])
        print("Deployed to origin/main")

    print(f"\nBatch publish complete ({len(social_files)} social JPGs in media library).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
