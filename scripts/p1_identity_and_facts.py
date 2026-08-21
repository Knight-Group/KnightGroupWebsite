#!/usr/bin/env python3
"""Second-audit P0/P1: identity, pricing examples, geo leaks, no URL changes.

Never interpolates seoTarget strings into sentences. City metas for
Hillsborough/Pasco must name that county, not Pinellas.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CITY_COUNTY: dict[str, tuple[str, str]] = {
    "tampa-handyman.html": ("Tampa", "Hillsborough County"),
    "town-n-country-handyman.html": ("Town 'n' Country", "Hillsborough County"),
    "westchase-handyman.html": ("Westchase", "Hillsborough County"),
    "citrus-park-handyman.html": ("Citrus Park", "Hillsborough County"),
    "carrollwood-handyman.html": ("Carrollwood", "Hillsborough County"),
    "northdale-handyman.html": ("Northdale", "Hillsborough County"),
    "egypt-lake-leto-handyman.html": ("Egypt Lake-Leto", "Hillsborough County"),
    "temple-terrace-handyman.html": ("Temple Terrace", "Hillsborough County"),
    "holiday-handyman.html": ("Holiday", "Pasco County"),
    "trinity-handyman.html": ("Trinity", "Pasco County"),
    "new-port-richey-handyman.html": ("New Port Richey", "Pasco County"),
    "elfers-handyman.html": ("Elfers", "Pasco County"),
    "seven-springs-handyman.html": ("Seven Springs", "Pasco County"),
    "jasmine-estates-handyman.html": ("Jasmine Estates", "Pasco County"),
    "beacon-square-handyman.html": ("Beacon Square", "Pasco County"),
    "port-richey-handyman.html": ("Port Richey", "Pasco County"),
    "land-o-lakes-handyman.html": ("Land O' Lakes", "Pasco County"),
}

REPLACEMENTS: list[tuple[str, str]] = [
    (
        '"jobTitle": "Co-Owner & Field Operations Lead",\n            "description": "Co-owner and Field Operations Lead of Knight Group Handyman Services LLC with journeyman plumbing experience and Florida property management background."',
        '"jobTitle": "Co-Owner & Field Operations Lead",\n            "description": "Co-owner and Field Operations Lead of Knight Group Handyman Services LLC with journeyman plumbing experience and Florida property management background."',
    ),
    (
        '"jobTitle": "Co-Owner & Field Operations Lead",',
        '"jobTitle": "Co-Owner & Field Operations Lead",',
    ),
    (
        "Co-owner and Field Operations Lead of Knight Group Handyman Services LLC with journeyman plumbing experience and Florida property management background.",
        "Co-owner and Field Operations Lead of Knight Group Handyman Services LLC with journeyman plumbing experience and Florida property management background.",
    ),
    (
        "Vince Knight, co-owner and Field Operations Lead of Knight Group Handyman Services in Safety Harbor, Florida",
        "Vince Knight, co-owner and Field Operations Lead of Knight Group Handyman Services in Safety Harbor, Florida",
    ),
    (
        "Vince Knight, co-owner and Field Operations Lead of Knight Group Handyman Services",
        "Vince Knight, co-owner and Field Operations Lead of Knight Group Handyman Services",
    ),
    (
        "Knight Group Handyman Services LLC is co-owned. Vince Knight is co-owner and Field Operations Lead, with 15 years as a journeyman plumber and 10 years in Florida property management. The other co-owner manages dispatch, technology, scheduling, and business systems.",
        "Knight Group Handyman Services LLC is co-owned. Vince Knight is co-owner and Field Operations Lead, with 15 years as a journeyman plumber and 10 years in Florida property management. The other co-owner manages dispatch, technology, scheduling, and business systems.",
    ),
    (
        "Vince Knight leads field standards, scope review, and complex-project support. Knight Group dispatches vetted local field professionals from Safety Harbor. You are not handed off to an anonymous call center.",
        "Vince Knight leads field standards, scope review, and complex-project support. Knight Group dispatches vetted local field professionals from Safety Harbor. You are not handed off to an anonymous call center.",
    ),
    (
        "Knight Group will review the scope and provide a no-obligation written estimate.",
        "Knight Group will review the scope and provide a no-obligation written estimate.",
    ),
    (
        "Standard visits are $150 for the first hour and $75 each additional hour. There is no two-hour minimum.",
        "Standard visits are $150 for the first hour and $75 each additional hour. There is no two-hour minimum.",
    ),
    (
        "you pay $150 for the first hour and $75 each additional hour, with no two-hour minimum",
        "you pay $150 for the first hour and $75 each additional hour, with no two-hour minimum",
    ),
    (
        "For larger scopes, hourly rates stay competitive after the first-hour charge. There is no two-hour minimum.",
        "For larger scopes, hourly rates stay competitive after the first-hour charge. There is no two-hour minimum.",
    ),
    (
        "That means a simple first-hour drywall patch or door adjustment can cost $240&ndash;$300 before add-on fees like service calls, travel charges, or steep materials markups.",
        "That means a simple first-hour drywall patch or door adjustment can cost $240&ndash;$300 before add-on fees like service calls, travel charges, or steep materials markups.",
    ),
    (
        "<li>Door adjustments, trim repair, and screen repair</li>",
        "<li>Door adjustments, trim repair, and screen repair</li>",
    ),
    (
        "<li>Large drywall repair and multi-stage carpentry</li>",
        "<li>Large drywall repair and multi-stage carpentry</li>",
    ),
    (
        "<li>Complex door and hardware correction</li>",
        "<li>Complex door and hardware correction</li>",
    ),
    (
        "<li>Higher-access work (ladders, heavy mounting)</li>",
        "<li>Higher-access work (ladders, heavy mounting)</li>",
    ),
    (
        "<li>Drywall patches, caulking, doors, and punch-list work</li>",
        "<li>Drywall patches, caulking, doors, and punch-list work</li>",
    ),
    (
        "<li>Leak diagnosis and licensed-plumber coordination when drinking-water connections are required</li>",
        "<li>Leak diagnosis and licensed-plumber coordination when drinking-water connections are required</li>",
    ),
    (
        "Short repair lists, drywall patches, door and trim work, and punch-list jobs are often the best-value calls because multiple items can be bundled into one visit.",
        "Short repair lists, drywall patches, door and trim work, and punch-list jobs are often the best-value calls because multiple items can be bundled into one visit.",
    ),
    (
        "Knight Group covers northwest Hillsborough on scheduled and expanding routes from Safety Harbor. Homeowners get a local insured crew for drywall, doors, carpentry, painting touch-ups, and punch-list repairs — not a referral marketplace. Licensed trades are coordinated when Florida DBPR requires it. Address confirmation is required; this is not a daily Pinellas-style loop across the whole county.",
        "Knight Group covers northwest Hillsborough on scheduled and expanding routes from Safety Harbor. Homeowners get a local insured crew for drywall, doors, carpentry, painting touch-ups, and punch-list repairs — not a referral marketplace. Licensed trades are coordinated when Florida DBPR requires it. Address confirmation is required; this is not a daily Pinellas-style loop across the whole county.",
    ),
    (
        "Hillsborough coverage focuses on northwest neighborhoods such as Westchase, Carrollwood, Citrus Park, Town 'n' Country, and nearby Tampa addresses that fit the current week’s route — not far south or east Hillsborough.",
        "Hillsborough coverage focuses on northwest neighborhoods such as Westchase, Carrollwood, Citrus Park, Town 'n' Country, and nearby Tampa addresses that fit the current week’s route — not far south or east Hillsborough.",
    ),
    (
        "We batch northwest Hillsborough work on planned bay crossings from Safety Harbor — Westchase, Carrollwood, and Citrus Park clusters reduce windshield time. Temple Terrace and similar edge addresses are confirmed first.",
        "We batch northwest Hillsborough work on planned bay crossings from Safety Harbor — Westchase, Carrollwood, and Citrus Park clusters reduce windshield time. Temple Terrace and similar edge addresses are confirmed first.",
    ),
    (
        "Knight Group covers west Pasco on scheduled route days from Safety Harbor. Homeowners get a local insured crew for drywall, doors, carpentry, painting touch-ups, and punch-list repairs — not a referral marketplace. Licensed trades are coordinated when Florida DBPR requires it. This is expanding coverage with address confirmation — not a daily county-wide loop.",
        "Knight Group covers west Pasco on scheduled route days from Safety Harbor. Homeowners get a local insured crew for drywall, doors, carpentry, painting touch-ups, and punch-list repairs — not a referral marketplace. Licensed trades are coordinated when Florida DBPR requires it. This is expanding coverage with address confirmation — not a daily county-wide loop.",
    ),
    (
        "West Pasco work is often chained on scheduled days through Holiday, New Port Richey, and Trinity. Land O' Lakes and similar inland addresses are accepted when they fit the route — confirm the address first.",
        "West Pasco work is often chained on scheduled days through Holiday, New Port Richey, and Trinity. Land O' Lakes and similar inland addresses are accepted when they fit the route — confirm the address first.",
    ),
    (
        "West Pasco is scheduled-route coverage from Safety Harbor, not a daily Pinellas-style loop. City pages list neighborhoods we visit most often — send the address if you are near a county line.",
        "West Pasco is scheduled-route coverage from Safety Harbor, not a daily Pinellas-style loop. City pages list neighborhoods we visit most often — send the address if you are near a county line.",
    ),
    (
        "Locally owned shop at 1225 7th St S — not a distant franchise dispatch desk.",
        "Locally owned shop at 1225 7th St S — not a distant franchise dispatch desk.",
    ),
    (
        "placeholder=\"Street, city, or area in Pinellas County\"",
        "placeholder=\"Street, city, or ZIP code\"",
    ),
    (
        "Quoted after intake for larger or custom properties (footprint, pool/spa, extra structures, reporting, or vendor coordination). We do not publish a one-size package until we see the house.",
        "Quoted after intake for larger or custom properties (footprint, pool/spa, extra structures, reporting, or vendor coordination). We do not publish a one-size package until we see the house.",
    ),
    (
        "moisture-damaged drywall repair",
        "moisture-damaged drywall repair",
    ),
    (
        "moisture-damaged drywall repair",
        "moisture-damaged drywall repair",
    ),
    (
        "Filter by plumbing, moisture-damaged drywall, renovations",
        "Filter by plumbing, moisture-damaged drywall, renovations",
    ),
    (
        "Vince Knight’s <strong>15 years of journeyman plumbing experience</strong> helps Knight Group recognize problems, perform lawful handyman-scope maintenance, and determine when a licensed plumber is required. Knight Group is not a licensed plumbing contractor.",
        "Vince Knight’s <strong>15 years of journeyman plumbing experience</strong> helps Knight Group recognize problems, perform lawful handyman-scope maintenance, and determine when a licensed plumber is required. Knight Group is not a licensed plumbing contractor.",
    ),
    (
        "Knight Group diagnoses fixture and leak issues, then refers licensed plumbers for work that connects to drinking water. We are registered and insured for handyman-scope maintenance and finish work around those repairs.",
        "Knight Group diagnoses fixture and leak issues, then refers licensed plumbers for work that connects to drinking water. We are registered and insured for handyman-scope maintenance and finish work around those repairs.",
    ),
    (
        "Plumbing diagnosis and lawful handyman-scope maintenance in Pinellas County. Drinking-water connections are referred to a licensed plumber.",
        "Plumbing diagnosis and lawful handyman-scope maintenance in Pinellas County. Drinking-water connections are referred to a licensed plumber.",
    ),
    (
        "Co-owner Vince Knight, Field Operations Lead, brings journeyman plumbing experience",
        "Co-owner Vince Knight, Field Operations Lead, brings journeyman plumbing experience",
    ),
    (
        "Vincent Knight — Co-Owner &amp; Field Operations Lead",
        "Vincent Knight — Co-Owner &amp; Field Operations Lead",
    ),
    (
        "<li>Leak observation, shutoff support, and licensed-plumber coordination</li>",
        "<li>Leak observation, shutoff support, and licensed-plumber coordination</li>",
    ),
    (
        "<li>Drywall, trim, doors, screens, and punch-list repairs</li>",
        "<li>Drywall, trim, doors, screens, and punch-list repairs</li>",
    ),
    (
        "<li>Cover-plate and bulb changes; electrical connections referred</li>",
        "<li>Cover-plate and bulb changes; electrical connections referred</li>",
    ),
    (
        "<li>Interior door adjustments, hardware, and window-screen repair</li>",
        "<li>Interior door adjustments, hardware, and window-screen repair</li>",
    ),
]


def natural_meta(city: str, county: str) -> str:
    return (
        f"{city} handyman for drywall, doors, punch-list repairs, and fixture diagnosis "
        f"in {county}. Registered and insured. Free written estimate."
    )


def fix_city_metas(changed: list[str]) -> None:
    for filename, (city, county) in CITY_COUNTY.items():
        path = ROOT / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        desc_m = re.search(r'<meta name="description" content="([^"]*)"', text, re.I)
        if not desc_m:
            continue
        current = desc_m.group(1)
        if "pinellas county" not in current.lower() and "pinellas" not in current.lower():
            continue
        new = natural_meta(city, county)
        updated = text.replace(current, new)
        # HTML-escaped city names in some metas
        if updated == text:
            continue
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))


def fix_meta_json() -> bool:
    path = ROOT / "seo" / "meta-descriptions.json"
    if not path.is_file():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    dirty = False
    for entry in data.get("pages", []):
        rel = str(entry.get("path") or "")
        name = Path(rel).name
        if name not in CITY_COUNTY:
            continue
        city, county = CITY_COUNTY[name]
        desc = str(entry.get("description") or "")
        if "pinellas" in desc.lower():
            entry["description"] = natural_meta(city, county)
            dirty = True
    if dirty:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dirty


def apply_replacements() -> list[str]:
    touched: list[str] = []
    for path in ROOT.rglob("*"):
        if path.suffix.lower() not in {".html", ".py", ".json", ".txt", ".md"}:
            continue
        if any(part in {"node_modules", ".git", "GalleryImages", "Images"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in REPLACEMENTS:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            touched.append(str(path.relative_to(ROOT)))
    return touched


def main() -> int:
    touched = apply_replacements()
    geo: list[str] = []
    fix_city_metas(geo)
    json_changed = fix_meta_json()
    print(f"string replacements: {len(touched)} files")
    for rel in touched[:80]:
        print(f"  {rel}")
    if len(touched) > 80:
        print(f"  … {len(touched) - 80} more")
    print(f"geo metas: {len(geo)} files")
    for rel in geo:
        print(f"  {rel}")
    print(f"meta-descriptions.json: {'updated' if json_changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
