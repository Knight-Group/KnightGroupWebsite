#!/usr/bin/env python3
"""Build gallery-manifest.json from renamed GalleryImages WebP files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "GalleryImages"
MANIFEST_PATH = GALLERY_DIR / "gallery-manifest.json"
SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff"}
WEBP_QUALITY = 85

# Curated copy keyed by exact WebP filename (after user renames).
IMAGE_CATALOG: dict[str, dict] = {
    "AC_Vent_Box.webp": {
        "group": "hvac-vent-boxing",
        "groupTitle": "HVAC vent boxing and sealing",
        "groupDescription": "Vent opening boxed, sealed, and finished so the repair blends cleanly into the surrounding wall.",
        "category": "general-repairs",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Vent area prepped and boxed",
        "description": "HVAC vent work with the surrounding area built out for a cleaner, more finished look.",
        "beforeAfter": False,
    },
    "Fixing_floor.webp": {
        "group": "floor-subfloor-repair",
        "groupTitle": "Rotted floor and subfloor repair",
        "groupDescription": "Damaged flooring torn back to sound material, then rebuilt so the repair could be closed out properly.",
        "category": "carpentry",
        "serviceLink": "/Services/carpentry-framing",
        "step": 1,
        "title": "Damaged flooring opened up",
        "description": "First stage of the job with rotted flooring removed and the repair area exposed.",
        "beforeAfter": False,
    },
    "fixing_floor2.webp": {
        "group": "floor-subfloor-repair",
        "step": 2,
        "title": "Subfloor repair in progress",
        "description": "Later stage of the same floor repair with new support and rebuild work underway.",
        "beforeAfter": False,
    },
    "GarbageDisposal.webp": {
        "group": "garbage-disposal-install",
        "groupTitle": "Garbage disposal installation",
        "groupDescription": "Under-sink disposal work completed as part of a practical plumbing repair call.",
        "category": "plumbing",
        "serviceLink": "/Services/plumbing-services",
        "step": 1,
        "title": "Garbage disposal installed",
        "description": "Completed disposal installation and hookup under the kitchen sink.",
        "beforeAfter": False,
    },
    "KnightGroup_before_after_drain.webp": {
        "group": "tub-drain-before-after",
        "groupTitle": "Tub drain repair — before & after",
        "groupDescription": "Side-by-side proof of a tub drain correction from the failed condition through the completed fix.",
        "category": "plumbing",
        "serviceLink": "/Services/plumbing-services",
        "step": 1,
        "title": "Tub drain before and after",
        "description": "Before-and-after comparison from a tub drain repair completed by Knight Group.",
        "beforeAfter": True,
    },
    "KnightGroupBeforeAfterPipes.webp": {
        "group": "pipe-repair-before-after",
        "groupTitle": "Pipe repair — before & after",
        "groupDescription": "Plumbing correction shown from the original problem through the finished repair.",
        "category": "plumbing",
        "serviceLink": "/Services/plumbing-services",
        "step": 1,
        "title": "Pipe repair before and after",
        "description": "Before-and-after photo from a pipe repair job in a local Pinellas County home.",
        "beforeAfter": True,
    },
    "KnightGroup_before_after_room.webp": {
        "group": "room-restoration-before-after",
        "groupTitle": "Room restoration — before & after",
        "groupDescription": "Interior room work shown from damage and tear-out through the restored finish.",
        "category": "renovations",
        "serviceLink": "/Services/home-renovations",
        "step": 1,
        "title": "Room restoration before and after",
        "description": "Before-and-after proof from a room rebuild and finish reset.",
        "beforeAfter": True,
    },
    "Moldy_Wall.webp": {
        "group": "mold-wall-repair",
        "groupTitle": "Mold damage on interior wall",
        "groupDescription": "Mold-affected wall shown from the initial discovery through later correction work on the same area.",
        "category": "mold-remediation",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Mold damage discovered on wall",
        "description": "Starting point of the job with visible mold damage that needed to be corrected before finish work could begin.",
        "beforeAfter": False,
    },
    "Moldy_Wall2.webp": {
        "group": "mold-wall-repair",
        "step": 2,
        "title": "Mold wall repair — later stage",
        "description": "Follow-up photo from the same mold wall job showing later progress on the correction.",
        "beforeAfter": False,
    },
    "Window_Wall.webp": {
        "group": "window-wall-repair",
        "groupTitle": "Window wall repair and rebuild",
        "groupDescription": "Window-area wall damage opened up, corrected, and rebuilt across multiple stages of the same job.",
        "category": "mold-remediation",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Window wall opened for repair",
        "description": "First stage with the window wall opened so damaged material could be removed and rebuilt.",
        "beforeAfter": False,
    },
    "Window_Wall2.webp": {
        "group": "window-wall-repair",
        "step": 2,
        "title": "Window wall rebuild progressing",
        "description": "Later stage of the same window-wall repair moving toward a finish-ready closeout.",
        "beforeAfter": False,
    },
    "OldTubDrain.webp": {
        "group": "tub-drain-replacement",
        "groupTitle": "Tub drain replacement",
        "groupDescription": "Failed tub drain removed and replaced — shown from the old assembly through the new install.",
        "category": "plumbing",
        "serviceLink": "/Services/plumbing-services",
        "step": 1,
        "title": "Original tub drain assembly",
        "description": "Starting point of the job with the old tub drain that needed replacement.",
        "beforeAfter": False,
    },
    "NewTubDrain.webp": {
        "group": "tub-drain-replacement",
        "step": 2,
        "title": "New tub drain installed",
        "description": "Completed tub drain replacement after the new assembly was installed.",
        "beforeAfter": False,
    },
    "Refinished Bathroom_Window.webp": {
        "group": "bathroom-tub-window-remodel",
        "groupTitle": "Bathroom tub surround, window, and floor work",
        "groupDescription": "Finished bathroom remodel with tile around the tub and window, updated faucet, window replacement, and new flooring.",
        "category": "renovations",
        "serviceLink": "/Services/home-renovations",
        "step": 1,
        "title": "Finished bathroom tub, window, and floor remodel",
        "description": "Completed bathroom update with tub surround tile, window work, faucet replacement, and new flooring.",
        "beforeAfter": False,
    },
    "Refinished_Bathroom.webp": {
        "group": "bathroom-remodel-cobblestone",
        "groupTitle": "Complete bathroom remodel",
        "groupDescription": "Full bathroom remodel with cobblestone flooring laid in the space and tile installed in the shower.",
        "category": "renovations",
        "serviceLink": "/Services/home-renovations",
        "step": 1,
        "title": "Complete bathroom remodel",
        "description": "Finished bathroom remodel with cobblestone flooring and shower tile installed throughout the space.",
        "beforeAfter": False,
    },
    "Refinished_Room.webp": {
        "group": "room-refinish",
        "groupTitle": "Interior room refinish",
        "groupDescription": "Room refinishing shown from the first completed view through a later stage of the same project.",
        "category": "painting",
        "serviceLink": "/Services/painting-finishing",
        "step": 1,
        "title": "Refinished room — first view",
        "description": "First photo from a room refinish with updated walls and a cleaner finished appearance.",
        "beforeAfter": False,
    },
    "Refinished_Room2.webp": {
        "group": "room-refinish",
        "step": 2,
        "title": "Refinished room — later stage",
        "description": "Second view from the same room refinish, showing later progress or another angle of the finished space.",
        "beforeAfter": False,
    },
    "before-after-fridge-wouldnt-close-does-now.webp": {
        "group": "fridge-door-alignment-before-after",
        "groupTitle": "Refrigerator door alignment — before & after",
        "groupDescription": "Refrigerator that would not close properly corrected so the door seals and operates normally again.",
        "category": "general-repairs",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Refrigerator door alignment before and after",
        "description": "Before-and-after proof from a fridge door repair so the unit closes and seals correctly.",
        "beforeAfter": True,
    },
    "before-after-broken-stove-burner-fixed.webp": {
        "group": "stove-burner-repair-before-after",
        "groupTitle": "Stove burner repair — before & after",
        "groupDescription": "Broken stove burner restored to safe, working condition.",
        "category": "general-repairs",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Stove burner repair before and after",
        "description": "Before-and-after photo from a kitchen stove burner repair completed in a Pinellas County home.",
        "beforeAfter": True,
    },
    "before-after-broken-blinds-replaced.webp": {
        "group": "blinds-replacement-before-after",
        "groupTitle": "Broken blinds replacement — before & after",
        "groupDescription": "Damaged window blinds removed and replaced with a clean, working set.",
        "category": "carpentry",
        "serviceLink": "/Services/carpentry-framing",
        "step": 1,
        "title": "Broken blinds replacement before and after",
        "description": "Before-and-after comparison from a window blind replacement job.",
        "beforeAfter": True,
    },
    "before-after-horney-removal-wall-sealed.webp": {
        "group": "hornet-removal-wall-sealed-before-after",
        "groupTitle": "Hornet nest removal and wall sealed — before & after",
        "groupDescription": "Hornet nest removed from the wall and the opening sealed and finished cleanly.",
        "category": "general-repairs",
        "serviceLink": "/Services/general-repairs",
        "step": 1,
        "title": "Hornet nest removal and wall sealed before and after",
        "description": "Before-and-after proof from hornet nest removal with the wall opening sealed and repaired.",
        "beforeAfter": True,
    },
}

SKIP_WEBP = {
    "MoldyWall.webp",  # Superseded by Moldy_Wall.webp
    "KnightGroup_before_after_after_pipes.webp",  # Duplicate of KnightGroupBeforeAfterPipes.webp
    "Refinishing_Bathroom_Window2.webp",  # Duplicate finished photo of bathroom-tub-window-remodel
}
LEGACY_NAME = re.compile(
    r"^(?:\d{8}_\d{6}|[0-9a-f]{8}-?)$",
    re.IGNORECASE,
)

CATEGORY_LABELS = {
    "all": "All projects",
    "plumbing": "Plumbing",
    "mold-remediation": "Mold & drywall",
    "carpentry": "Carpentry & floors",
    "renovations": "Renovations",
    "painting": "Painting & finishing",
    "general-repairs": "General repairs",
}


def is_before_after_filename(filename: str) -> bool:
    lower = Path(filename).stem.lower()
    return bool(re.search(r"before[_\s-]*and[_\s-]*after|before[_\s-]*after|beforeafter", lower))


def progression_key(filename: str) -> str:
    stem = Path(filename).stem.lower().replace(" ", "_")
    if stem.endswith("2"):
        return stem[:-1].rstrip("_")
    return stem


def infer_step(filename: str) -> int:
    stem = Path(filename).stem.lower()
    if stem.startswith("old") and "tub" in stem:
        return 1
    if stem.startswith("new") and "tub" in stem:
        return 2
    if stem.endswith("2"):
        return 2
    return 1


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "Project photo"


def is_legacy_asset(filename: str) -> bool:
    stem = Path(filename).stem
    return bool(LEGACY_NAME.match(stem))


def should_list_in_gallery(filename: str) -> bool:
    if filename in SKIP_WEBP or filename == MANIFEST_PATH.name:
        return False
    return filename in IMAGE_CATALOG


def convert_sources() -> int:
    converted = 0
    for path in sorted(GALLERY_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTS:
            continue
        if is_legacy_asset(path.name):
            continue
        target = path.with_suffix(".webp")
        if target.exists() and target.stat().st_mtime >= path.stat().st_mtime:
            continue
        with Image.open(path) as image:
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
            image.save(target, "WEBP", quality=WEBP_QUALITY, method=6)
        converted += 1
    return converted


def group_anchor_meta(group_id: str) -> dict:
    for item in IMAGE_CATALOG.values():
        if item.get("group") == group_id and item.get("groupTitle"):
            return item
    return {}


def build_image_entry(filename: str) -> dict:
    meta = dict(IMAGE_CATALOG.get(filename, {}))
    if meta.get("group"):
        anchor = group_anchor_meta(meta["group"])
        for key in ("category", "serviceLink", "groupTitle", "groupDescription"):
            meta.setdefault(key, anchor.get(key))

    title = meta.get("title", title_from_filename(filename))
    entry = {
        "src": f"GalleryImages/{filename}",
        "filename": filename,
        "group": meta.get("group", progression_key(filename)),
        "step": meta.get("step", infer_step(filename)),
        "title": title,
        "seoAlt": f"{title} — handyman project photo in Pinellas County FL by Knight Group",
        "description": meta.get(
            "description",
            "Completed handyman work from a Knight Group project in Pinellas County.",
        ),
        "category": meta.get("category", "general-repairs"),
        "serviceLink": meta.get("serviceLink", "/Services/general-repairs"),
        "beforeAfter": meta.get("beforeAfter", is_before_after_filename(filename)),
        "groupTitle": meta.get("groupTitle"),
        "groupDescription": meta.get("groupDescription"),
    }
    return entry


def build_groups(images: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for image in images:
        grouped.setdefault(image["group"], []).append(image)

    groups = []
    for group_id in sorted(grouped.keys(), key=lambda gid: grouped[gid][0].get("groupTitle") or gid):
        items = sorted(grouped[group_id], key=lambda img: (img["step"], img["filename"].lower()))
        first = items[0]
        groups.append(
            {
                "id": group_id,
                "title": first.get("groupTitle") or first["title"],
                "description": first.get("groupDescription") or first["description"],
                "category": first["category"],
                "serviceLink": first["serviceLink"],
                "beforeAfter": any(img["beforeAfter"] for img in items),
                "progression": len(items) > 1 and not any(img["beforeAfter"] for img in items),
                "images": [
                    {
                        "src": img["src"],
                        "filename": img["filename"],
                        "step": img["step"],
                        "title": img["title"],
                        "seoAlt": img.get("seoAlt", img["title"]),
                        "description": img["description"],
                        "beforeAfter": img["beforeAfter"],
                    }
                    for img in items
                ],
            }
        )
    return groups


def main() -> None:
    converted = convert_sources()

    images = []
    for filename in sorted(IMAGE_CATALOG.keys()):
        path = GALLERY_DIR / filename
        if not path.is_file():
            print(f"Warning: missing catalog image {filename}")
            continue
        images.append(build_image_entry(filename))

    groups = build_groups(images)
    manifest = {
        "generated": True,
        "categories": [{"id": key, "label": label} for key, label in CATEGORY_LABELS.items()],
        "groups": groups,
        "images": images,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Converted {converted} source file(s) to WebP.")
    print(f"Wrote {len(groups)} project group(s) / {len(images)} image(s) to {MANIFEST_PATH.name}.")


if __name__ == "__main__":
    main()
