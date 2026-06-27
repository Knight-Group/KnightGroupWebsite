#!/usr/bin/env python3
"""Download city/county landmark images from Wikipedia lead photos."""

from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

from city_landmark_catalog import LANDMARK_LABELS, WIKI_JSON
from geo_city_data import CITY_PROFILES
from seo_page_data import COUNTY_REGIONS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Images" / "cities"


def verify_url(url: str) -> None:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "KnightGroupWebsite/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc


def download_image(url: str, retries: int = 4) -> Image.Image:
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            verify_url(url)
            req = urllib.request.Request(url, headers={"User-Agent": "KnightGroupWebsite/1.0"})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) < 3000:
                raise RuntimeError("response too small")
            return Image.open(io.BytesIO(data)).convert("RGB")
        except Exception as exc:
            last_exc = exc
            if "429" in str(exc) and attempt < retries - 1:
                wait = 8 * (attempt + 1)
                print(f"rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
    raise last_exc or RuntimeError("download failed")


def save_resized(img: Image.Image, slug: str) -> None:
    img = img.resize((900, 600), Image.Resampling.LANCZOS)
    img.save(OUT / f"{slug}.webp", "WEBP", quality=84, method=6)
    img.save(OUT / f"{slug}.jpg", "JPEG", quality=86, optimize=True)
    print(f"saved {slug}")


def load_catalog() -> dict[str, dict]:
    if not WIKI_JSON.is_file():
        raise FileNotFoundError(
            f"Missing {WIKI_JSON.name} — run: python scripts/fetch_wiki_landmarks.py"
        )
    return json.loads(WIKI_JSON.read_text(encoding="utf-8"))


def main() -> int:
    catalog = load_catalog()
    OUT.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    targets = list(CITY_PROFILES.keys()) + [r["hub_slug"] for r in COUNTY_REGIONS]
    for slug in targets:
        entry = catalog.get(slug)
        if not entry or not entry.get("url"):
            failures.append(f"{slug}: no Wikipedia image in catalog")
            continue
        try:
            save_resized(download_image(entry["url"]), slug)
            entry["landmark"] = LANDMARK_LABELS.get(slug, entry.get("landmark", slug))
            time.sleep(3)
        except Exception as exc:
            failures.append(f"{slug}: {exc}")
            print(f"failed {slug}: {exc}", file=sys.stderr)

    WIKI_JSON.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    if failures:
        print(f"\n{len(failures)} failures:", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print(f"OK — {len(targets)} landmark images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
