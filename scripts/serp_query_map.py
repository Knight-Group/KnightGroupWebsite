#!/usr/bin/env python3
"""Build Serper.dev PAGE_QUERY_MAP dynamically for all site sections."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from geo_serp_keywords import (  # noqa: E402
    CITY_PRIMARY_QUERY,
    CITY_SECONDARY,
    COMBO_PRIMARY_QUERY,
    COUNTY_PRIMARY_QUERY,
    COUNTY_SECONDARY,
)
from seo_page_data import CITY_COMBOS, COUNTY_REGIONS, NICHE_SERVICES, PRICING_PAGES  # noqa: E402

LOCATION_BY_COUNTY = {
    "pinellas": "Pinellas County, Florida, United States",
    "hillsborough": "Hillsborough County, Florida, United States",
    "pasco": "Pasco County, Florida, United States",
}

DEFAULT_LOCATION = LOCATION_BY_COUNTY["pinellas"]

# Core static + major service pages (queries unchanged from original research).
CORE_PAGE_QUERIES: dict[str, list[str]] = {
    "index.html": ["knight group", "knightgroup", "handyman pinellas county"],
    "services.html": ["handyman services pinellas county"],
    "pricing.html": ["handyman prices pinellas county", "handyman near me prices"],
    "booking.html": ["handyman estimate pinellas county"],
    "contact.html": ["knight group handyman contact"],
    "about.html": ["knight group handyman", "knight services llc", "knights handyman services"],
    "galleries.html": ["handyman projects pinellas county"],
    "service-areas.html": ["handyman service areas pinellas county"],
    "Services/handyman.html": [
        "handyman company pinellas",
        "handyman pinellas county fl",
        "handyman near me small jobs",
    ],
    "Services/general-repairs.html": ["handyman pinellas county", "general home repairs pinellas"],
    "Services/plumbing-services.html": [
        "sink repair clearwater",
        "plumbing services in pinellas county",
        "plumbing repair clearwater fl",
    ],
    "Services/carpentry-framing.html": ["carpentry services near me", "carpenter pinellas county"],
    "Services/doors-windows.html": ["door repair pinellas county", "window repair clearwater"],
    "Services/electrical-work.html": ["handyman electrical work pinellas county"],
    "Services/emergency-services.html": ["emergency handyman pinellas county"],
    "Services/home-renovations.html": ["small home renovations pinellas county"],
    "Services/painting-finishing.html": ["handyman painting pinellas county"],
    "Services/custom-projects.html": ["custom handyman projects pinellas county"],
}


def county_slug_for_city(city_slug: str) -> str:
    for region in COUNTY_REGIONS:
        for city in region["cities"]:
            if city["slug"] == city_slug:
                return region["hub_slug"]
    return "pinellas"


def build_full_page_query_map() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = dict(CORE_PAGE_QUERIES)

    for region in COUNTY_REGIONS:
        hub_slug = region["hub_slug"]
        county_file = f"{hub_slug}-handyman.html"
        primary = COUNTY_PRIMARY_QUERY.get(hub_slug, f"handyman {region['hub_name'].lower()}")
        secondary = COUNTY_SECONDARY.get(hub_slug, [])
        mapping[county_file] = [primary, *secondary[:2]]

        for city in region["cities"]:
            city_slug = city["slug"]
            city_file = f"{city_slug}-handyman.html"
            queries = [CITY_PRIMARY_QUERY.get(city_slug, f"{city['name'].lower()} handyman")]
            secondary_city = CITY_SECONDARY.get(city_slug, [])
            if secondary_city:
                queries.append(secondary_city[0])
            mapping[city_file] = queries[:3]

    for combo_slug, _service_slug, city_name, _label, _parent, _niche in CITY_COMBOS:
        combo_file = f"{combo_slug}.html"
        primary = COMBO_PRIMARY_QUERY.get(combo_slug, f"{_label} {city_name.lower()}")
        mapping[combo_file] = [primary]

    extra_combos = [
        "palm-harbor-drywall-repair",
        "largo-toilet-repair",
        "oldsmar-door-adjustment",
        "dunedin-trim-repair",
        "seminole-interior-painting",
    ]
    for combo_slug in extra_combos:
        if combo_slug not in mapping:
            mapping[f"{combo_slug}.html"] = [COMBO_PRIMARY_QUERY.get(combo_slug, combo_slug.replace("-", " "))]

    for defn in NICHE_SERVICES:
        path = f"Services/{defn['slug']}.html"
        queries = list(defn.get("queries") or [])
        if not queries:
            queries = [defn["h1"].lower()]
        mapping[path] = queries[:3]

    for defn in PRICING_PAGES:
        slug = defn["slug"].replace("pricing-", "")
        path = f"pricing-{slug}.html"
        topic = defn["h1"].lower()
        mapping[path] = [topic, "handyman near me prices"]

    gallery_detail_pages = [
        "bathroom-tub-window-remodel",
        "blinds-replacement-before-after",
        "bathroom-remodel-cobblestone",
        "garbage-disposal-install",
        "mold-wall-repair",
        "pipe-repair-before-after",
        "floor-subfloor-repair",
        "tub-drain-replacement",
    ]
    for gallery_slug in gallery_detail_pages:
        mapping[f"gallery/{gallery_slug}.html"] = [gallery_slug.replace("-", " "), "handyman projects pinellas county"]

    return mapping


def query_locations(page_path: str) -> str:
    if page_path.endswith("-handyman.html"):
        slug = page_path.removesuffix("-handyman.html")
        for region in COUNTY_REGIONS:
            if region["hub_slug"] == slug:
                return LOCATION_BY_COUNTY[region["hub_slug"]]
            for city in region["cities"]:
                if city["slug"] == slug:
                    return LOCATION_BY_COUNTY[region["hub_slug"]]
    for county_slug, location in LOCATION_BY_COUNTY.items():
        if page_path.startswith(county_slug) or f"/{county_slug}-" in page_path:
            return location
    for combo_slug, city_slug, *_rest in CITY_COMBOS:
        if page_path == f"{combo_slug}.html":
            return LOCATION_BY_COUNTY[county_slug_for_city(city_slug)]
    return DEFAULT_LOCATION
