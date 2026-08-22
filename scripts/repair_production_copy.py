#!/usr/bin/env python3
"""Repair production copy, metadata, and commercial scope claims from Knight Group facts.

Does not rewrite gallery project evidence. Competitor SERP text is never copied.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_detail_copy import gallery_meta  # noqa: E402
from page_meta import clip_at_word_boundary  # noqa: E402

ROOT = SCRIPT_DIR.parent
SKIP_DIRS = {"gallery", "scripts", "admin", "docs", "node_modules", ".github", "legacy"}

COMPETITOR_MARKERS = (
    "reel construction",
    "specialties:",
    "family based construction",
    "trusted general contractor",
    "memphis, tn",
    "amarillo",
    "washington dc",
)

META_OVERRIDES = {
    "Services/home-renovations.html": (
        "Bathroom refreshes, flooring, tile, and finish work in Pinellas County. "
        "Licensed trades referred when required. Free written estimate."
    ),
    "Services/water-damage-repair.html": (
        "Post-leak drywall and finish repair in Pinellas County after the water source is stopped. "
        "Registered and insured. Free written estimate."
    ),
    "Services/doors-windows.html": (
        "Door adjustments, locks, screens, and weatherstripping in Pinellas County. "
        "Full window and new exterior-door replacement is referred. Free written estimate."
    ),
    "Services/emergency-services.html": (
        "Urgent property-damage response in Pinellas County during posted hours and after-hours callback. "
        "Not a 24/7 dispatch service. Call (813) 649-3341."
    ),
    "Services/electrical-work.html": (
        "Ceiling fans, light fixtures, switches, and outlet swaps in Pinellas County on existing circuits. "
        "Not a licensed electrician. Free written estimate."
    ),
    "Services/plumbing-services.html": (
        "Faucet, toilet, sink, and fixture plumbing in Pinellas County. Not a licensed plumbing contractor; "
        "repipes and sewer work are referred. Free written estimate."
    ),
    "Services/handyman.html": (
        "Registered Safety Harbor handyman for Pinellas County drywall, doors, carpentry, painting, and punch lists. "
        "Free written estimate."
    ),
    "pricing.html": (
        "Handyman pricing: $150 first hour, $75 after. Specialty $200/$100. No two-hour minimum. "
        "Pinellas County. Free written estimate."
    ),
    "hillsborough-handyman.html": (
        "Hillsborough County handyman for Tampa, Temple Terrace, Westchase, and northwest routes. "
        "Lutz / North Tampa by confirmation. No Lutz office."
    ),
    "services.html": (
        "Handyman services in Tampa Bay: repairs, drywall, carpentry, painting, doors, Home Watch, and licensed-trade coordination."
    ),
    "service-areas.html": (
        "Handyman service areas across Pinellas, Hillsborough, and west Pasco — including Temple Terrace. Lutz / North Tampa by confirmation. No Lutz office."
    ),
    "pricing-handyman-by-the-hour.html": (
        "Hourly handyman rates in Pinellas County: $150 first hour and $75 after. No two-hour minimum. Free written estimate."
    ),
    "galleries.html": (
        "Real Knight Group project photos from Pinellas County homes: drywall, doors, carpentry, painting, and punch-list repairs."
    ),
    "largo-handyman.html": (
        "Largo handyman from Safety Harbor: drywall, doors, paint-ready finish work, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "handyman-scope-florida.html": (
        "Florida handyman scope: Knight Group is registered and insured, not a licensed plumber, electrician, or GC. Licensed trades are referred when required."
    ),
    "hurricane-repair-handyman-pinellas.html": (
        "Storm follow-up, weatherproofing, and post-leak drywall in Pinellas County. Roofing, electrical, and structural work are referred."
    ),
    "plumber-background-handyman.html": (
        "Vince Knight’s journeyman plumbing background supports diagnosis. Knight Group is not a licensed plumbing contractor. Potable-water work is referred."
    ),
    "rental-turnover-handyman.html": (
        "Rental turnover punch lists in Pinellas County: drywall, doors, paint, screens, and hardware. Licensed trades referred when required."
    ),
}

OWNER_REPLACEMENTS = [
    (
        "Knight Group Handyman Services LLC is owner-operated in Safety Harbor",
        "Knight Group is locally co-owned and centrally managed from Safety Harbor",
    ),
    (
        "Knight Group is owner-operated in Safety Harbor",
        "Knight Group is locally co-owned and centrally managed from Safety Harbor",
    ),
    (
        "You work directly with the owner — not a rotating anonymous technician.",
        "Vince Knight serves as Co-Owner & Field Operations Lead, with vetted local field professionals dispatched from Safety Harbor.",
    ),
    (
        "You work directly with the owner — not a distant call center.",
        "You work with a locally co-owned Safety Harbor team — not a distant call center.",
    ),
    (
        "you work directly with the owner",
        "you work with a locally co-owned Safety Harbor team",
    ),
    ("Vince Knight, owner of", "Vince Knight, Co-Owner & Field Operations Lead of"),
    ("Vince Knight, owner", "Vince Knight, Co-Owner & Field Operations Lead"),
    ("is owner-operated", "is locally co-owned and centrally managed"),
    ("Owner-operated", "Locally co-owned"),
    ("owner-operated", "locally co-owned"),
]

COMMERCIAL_REPLACEMENTS = [
    (
        "around-the-clock emergency services",
        "posted-hours and after-hours callback response",
    ),
    (
        "around-the-clock emergency",
        "after-hours callback",
    ),
    (
        "provides around-the-clock",
        "provides posted-hours and after-hours callback",
    ),
    (
        "full window unit swaps",
        "screen, hardware, and weatherstripping repairs; full window-unit replacement is referred",
    ),
    (
        "Yes — we handle window glass replacement, frame repair, weatherstripping, and screen, hardware, and weatherstripping repairs; full window-unit replacement is referred for standard residential windows.",
        "We handle screen, hardware, weatherstripping, and eligible window maintenance. Full window-unit replacement is referred when licensed or permitted work is required.",
    ),
    (
        "$75 per additional hour for common handyman repairs, punch-list work, drywall patches, door adjustments, caulking, screens, and shelving.",
        "$75 per additional hour for common handyman repairs, punch-list work, fixture swaps, caulking, sealing, and small drywall patches.",
    ),
    (
        "Visible leak assessment, finish closeout, and licensed-plumber coordination when potable-water work is required",
        "Faucets, shutoffs, fixtures, and small leaks on existing connections",
    ),
    (
        "Eligible hardware and finish repairs",
        "Fixture swaps",
    ),
    (
        "eligible hardware and finish repairs",
        "fixture swaps",
    ),
    (
        "heavier mounting and carpentry",
        "fixture installs",
    ),
]


def is_contaminated(text: str) -> bool:
    lowered = text.lower()
    if any(marker in lowered for marker in COMPETITOR_MARKERS):
        return True
    if "..." in text:
        return True
    if re.search(r"\b\w{1,3}\.\.\.\s*$", text):
        return True
    if re.search(r"\bes\.\.\.\s*$", lowered):
        return True
    return False


def fallback_meta(path: str, current: str) -> str:
    if path.startswith("gallery/") and path.endswith(".html"):
        slug = Path(path).stem
        gallery = gallery_meta(slug, "")
        if gallery:
            return clip_at_word_boundary(gallery)
    if path in META_OVERRIDES:
        return clip_at_word_boundary(META_OVERRIDES[path])
    if path.startswith("Services/"):
        slug = Path(path).stem.replace("-", " ")
        return clip_at_word_boundary(
            f"{slug.title()} from Knight Group in Safety Harbor and Pinellas County. "
            "Registered and insured. Free written estimate."
        )
    if path.endswith("-handyman.html"):
        city = Path(path).stem.replace("-handyman", "").replace("-", " ").title()
        return clip_at_word_boundary(
            f"{city} handyman from Safety Harbor: drywall, doors, caulk, screens, and punch-list repairs. "
            "Free written estimate."
        )
    if is_contaminated(current) or not current.strip():
        return clip_at_word_boundary(
            "Knight Group Handyman Services in Safety Harbor, Florida. Registered and insured. Free written estimate."
        )
    return clip_at_word_boundary(current)


def repair_meta_json() -> int:
    path = ROOT / "seo" / "meta-descriptions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    pages = data.setdefault("pages", [])
    by_path = {str(entry.get("path")): entry for entry in pages}
    changed = 0
    for rel, description in META_OVERRIDES.items():
        repaired = clip_at_word_boundary(description)
        if rel in by_path:
            if by_path[rel].get("description") != repaired:
                by_path[rel]["description"] = repaired
                changed += 1
        else:
            pages.append({"path": rel, "gsc_queries": [], "serper_note": "", "description": repaired})
            changed += 1
    for entry in pages:
        current = str(entry.get("description") or "")
        repaired = fallback_meta(str(entry.get("path") or ""), current)
        if repaired != current:
            entry["description"] = repaired
            changed += 1
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return changed


def unescape_broken_markup(text: str) -> str:
    return (
        text.replace("&lt;strong&gt;", "<strong>")
        .replace("&lt;/strong&gt;", "</strong>")
        .replace("&lt;a href=&quot;/pricing&quot;&gt;", '<a href="/pricing">')
        .replace("&lt;a href=&quot;/pricing-handyman-by-the-hour&quot;&gt;", '<a href="/pricing-handyman-by-the-hour">')
        .replace("&lt;/a&gt;", "</a>")
    )


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def public_html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0].lower() in SKIP_DIRS:
            continue
        if any(part.lower() in SKIP_DIRS for part in rel.parts):
            continue
        files.append(path)
    return files


def repair_html() -> int:
    changed = 0
    for path in public_html_files():
        original = path.read_text(encoding="utf-8")
        text = unescape_broken_markup(original)
        text = apply_replacements(text, OWNER_REPLACEMENTS + COMMERCIAL_REPLACEMENTS)
        if path.name == "pricing-no-2-hour-minimum.html":
            text = text.replace(
                "a single faucet swap, door adjustment, shelf install, or caulk refresh",
                "a door adjustment, shelf install, caulk refresh, drywall patch or screen repair",
            )
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def repair_generators() -> None:
    targets = [
        ROOT / "scripts" / "service-expansions.py",
        ROOT / "scripts" / "service_expansions.py",
        ROOT / "scripts" / "niche_expansions.py",
    ]
    for path in targets:
        if not path.is_file():
            continue
        text = apply_replacements(path.read_text(encoding="utf-8"), OWNER_REPLACEMENTS)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    meta_changed = repair_meta_json()
    repair_generators()
    html_changed = repair_html()
    print(f"Repaired {meta_changed} meta descriptions and {html_changed} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
