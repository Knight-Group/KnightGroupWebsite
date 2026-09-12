"""Export a landscape About-card crop that keeps Vince's face in frame."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Images" / "KGHero_person_crop_1200x1600.jpg"
DEST = ROOT / "Images" / "related" / "about-vince-face.webp"
CARD = (800, 600)


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(SRC) as image:
        rgb = image.convert("RGB")
        src_w, src_h = rgb.size
        target_w, target_h = CARD
        crop_h = max(1, int(src_w * target_h / target_w))
        rgb = rgb.crop((0, 0, src_w, min(src_h, crop_h)))
        rgb = rgb.resize(CARD, Image.Resampling.LANCZOS)
        rgb.save(DEST, "WEBP", quality=86, method=6)
    print(f"wrote {DEST.relative_to(ROOT)} from top {crop_h}px of {SRC.name}")


if __name__ == "__main__":
    main()
