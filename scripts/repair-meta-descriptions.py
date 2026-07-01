#!/usr/bin/env python3
"""Repair low-quality Serper-derived meta descriptions in seo/meta-descriptions.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from page_meta import clip_meta  # noqa: E402
from seo_page_data import NICHE_SERVICES, PRICING_PAGES  # noqa: E402

ROOT = SCRIPT_DIR.parent
META_PATH = ROOT / "seo" / "meta-descriptions.json"

BAD_PATTERNS = [
    re.compile(r"Memphis,\s*TN", re.I),
    re.compile(r"colorado-", re.I),
    re.compile(r"Quality home\s*\.", re.I),
    re.compile(r"in Clear\.", re.I),
    re.compile(r"With Real\.", re.I),
    re.compile(r"From trim to cust\.", re.I),
    re.compile(r"Amarillo", re.I),
    re.compile(r"Washington DC", re.I),
]

MAJOR_SERVICE_META = {
    "Services/handyman.html": (
        "Registered Safety Harbor handyman serving Pinellas County. Drywall, plumbing fixtures, doors, "
        "paint, and punch-list repairs from $75/hr with no 2-hour minimum. Free written estimate."
    ),
    "Services/general-repairs.html": (
        "General home repairs in Pinellas County: drywall patches, leak damage, doors, caulking, and "
        "punch-list work. No 2-hour minimum. Registered and insured. Free written estimate."
    ),
    "Services/plumbing-services.html": (
        "Fixture plumbing in Pinellas County: faucets, toilets, disposals, drains, and minor leak fixes. "
        "Owner has journeyman plumbing background. Registered and insured. Free estimate."
    ),
    "Services/electrical-work.html": (
        "Handyman electrical in Pinellas County: ceiling fans, fixtures, switches, and like-for-like "
        "replacements on existing circuits. Registered and insured. Free written estimate."
    ),
    "Services/carpentry-framing.html": (
        "Carpentry and framing in Pinellas County: trim, shelving, fence boards, door frames, and small "
        "structural repairs. Registered and insured. Free written estimate."
    ),
    "Services/painting-finishing.html": (
        "Interior painting and finish work in Pinellas County: rooms, trim, touch-ups, and drywall "
        "texture matching. Registered and insured. Free written estimate."
    ),
    "Services/home-renovations.html": (
        "Smaller home renovation scopes in Pinellas County: baths, rooms, and finish packages without "
        "full GC overhead. Registered and insured. Free written estimate."
    ),
    "Services/doors-windows.html": (
        "Door and window handyman work in Pinellas County: adjustments, hardware, screens, and minor "
        "frame repairs. Registered and insured. Free written estimate."
    ),
    "Services/custom-projects.html": (
        "Custom handyman projects in Pinellas County: built-ins, shelving, accent walls, and one-off "
        "home improvements. Registered and insured. Free written estimate."
    ),
    "Services/emergency-services.html": (
        "Emergency handyman response in Pinellas County for active leaks, storm damage, and urgent "
        "repairs. Call (813) 649-3341. Registered and insured. Free estimate when safe to quote."
    ),
    "index.html": (
        "Registered Safety Harbor handyman team serving Pinellas County. Plumbing, drywall, carpentry, "
        "painting and punch-list repairs. Free written estimate."
    ),
    "services.html": (
        "Handyman services across Pinellas County: repairs, plumbing fixtures, electrical swaps, "
        "carpentry, painting, doors, windows, and emergency calls. Free written estimate."
    ),
    "service-areas.html": (
        "Knight Group serves Safety Harbor, Clearwater, Dunedin, Palm Harbor, Largo, Tampa Bay, and "
        "nearby Pinellas, Hillsborough, and Pasco communities. Confirm your city. Free estimate."
    ),
    "pricing.html": (
        "Transparent handyman pricing in Pinellas County: $75–$150/hr with no 2-hour minimum, plus "
        "flat-rate quotes for defined scopes. Materials markup 10%. Free written estimate."
    ),
    "pricing-handyman-by-the-hour.html": (
        "Handyman by the hour in Pinellas County from $75–$150 with no 2-hour minimum. Ideal for punch "
        "lists and mixed small repairs. Registered and insured. Free written estimate."
    ),
    "pricing-flat-rate-handyman.html": (
        "Flat-rate handyman quotes in Pinellas County for defined scopes after photos or a short visit. "
        "Know the number before work starts. Registered and insured. Free written estimate."
    ),
    "pricing-plumbing-repair-prices.html": (
        "Handyman plumbing prices in Pinellas County for faucets, toilets, disposals, and minor leaks "
        "within fixture scope. Journeyman-plumber owner. Free written estimate."
    ),
    "pricing-no-2-hour-minimum.html": (
        "No 2-hour minimum handyman in Pinellas County. Pay only for time worked from $75/hr — unlike "
        "franchise $150+ two-hour minimums. Registered and insured. Free estimate."
    ),
}

NICHE_BY_PATH = {f"Services/{item['slug']}.html": item for item in NICHE_SERVICES}
PRICING_BY_PATH = {f"{item['slug']}.html": item for item in PRICING_PAGES}


def is_low_quality(description: str) -> bool:
    text = description.strip()
    if not text:
        return True
    if any(pattern.search(text) for pattern in BAD_PATTERNS):
        return True
    if text.count("Registered & insured. Free estimate.") and len(text) < 130:
        return True
    if "Knight Group — registered Safety Harbor handyman team. Free estimate." in text:
        return True
    return False


def niche_meta(defn: dict) -> str:
    label = defn["h1"].strip().rstrip(".")
    lead = defn["lead"].strip()
    first = lead.split(".")[0].strip()
    if first and first[0].islower():
        first = first[0].upper() + first[1:]
    return clip_meta(f"{label} in Pinellas County. {first}. Registered and insured. Free written estimate.")


def fallback_for(path: str) -> str | None:
    if path in MAJOR_SERVICE_META:
        return clip_meta(MAJOR_SERVICE_META[path])
    if path in NICHE_BY_PATH:
        return niche_meta(NICHE_BY_PATH[path])
    if path in PRICING_BY_PATH:
        item = PRICING_BY_PATH[path]
        return clip_meta(
            f"{item['h1'].title()} in Pinellas County. {item['lead'].split('.')[0].strip()}. "
            "Registered and insured. Free written estimate."
        )
    return None


def main() -> int:
    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    repaired = 0
    for entry in data.get("pages", []):
        path = str(entry.get("path") or "")
        desc = str(entry.get("description") or "").strip()
        if not is_low_quality(desc):
            continue
        replacement = fallback_for(path)
        if not replacement:
            continue
        entry["description"] = replacement
        entry["serper_note"] = (entry.get("serper_note") or "") + " [repaired bad meta]"
        repaired += 1
        print(f"repaired: {path}")

    META_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Done. {repaired} descriptions repaired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
