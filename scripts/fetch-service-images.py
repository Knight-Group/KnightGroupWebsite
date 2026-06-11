#!/usr/bin/env python3
"""Download topic-matched service card images as WebP + JPEG."""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Images" / "services"

# Pexels + Unsplash (free to use). Each slug maps to a vetted, topic-specific photo.
IMAGES = {
    # Handyman in hard hat working on site
    "handyman": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=900&q=80",
    "general-repairs": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=900&q=80",
    # Bathroom sink + toilet
    "plumbing-services": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=900&q=80",
    # Keep — user approved homepage electrical card
    "electrical-work": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=900&q=80",
    # Wall-mounted crate shelving
    "carpentry-framing": "https://images.pexels.com/photos/1090638/pexels-photo-1090638.jpeg?auto=compress&cs=tinysrgb&w=900",
    "painting-finishing": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?auto=format&fit=crop&w=900&q=80",
    # Flashy renovated open-plan interior
    "home-renovations": "https://images.pexels.com/photos/259962/pexels-photo-259962.jpeg?auto=compress&cs=tinysrgb&w=900",
    # Modern room with glass door + large window
    "doors-windows": "https://images.pexels.com/photos/1571458/pexels-photo-1571458.jpeg?auto=compress&cs=tinysrgb&w=900",
    # Drywall / taping handyman job
    "custom-projects": "https://images.pexels.com/photos/5691603/pexels-photo-5691603.jpeg?auto=compress&cs=tinysrgb&w=900",
    # Room mid-renovation — door off hinges, tools, drop cloths
    "emergency-services": "https://images.pexels.com/photos/5691549/pexels-photo-5691549.jpeg?auto=compress&cs=tinysrgb&w=900",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, url in IMAGES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img = img.resize((800, 600), Image.Resampling.LANCZOS)
        img.save(OUT / f"{slug}.webp", "WEBP", quality=84, method=6)
        img.save(OUT / f"{slug}.jpg", "JPEG", quality=86, optimize=True)
        print(f"saved {slug}")


if __name__ == "__main__":
    main()
