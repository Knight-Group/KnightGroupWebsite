"""Serper.dev SERP keyword map for geo pages — sourced from seo/serp-meta-research.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERP_JSON = ROOT / "seo" / "serp-meta-research.json"

# Direct Serper queries mapped to city / county / combo slugs (from serp-meta-research.py PAGE_QUERY_MAP).
CITY_PRIMARY_QUERY: dict[str, str] = {
    "safety-harbor": "knight group handyman",
    "clearwater": "clearwater handyman",
    "dunedin": "handyman company pinellas",
    "palm-harbor": "handyman pinellas county",
    "largo": "handyman pinellas county fl",
    "oldsmar": "handyman near me small jobs",
    "tarpon-springs": "plumbing services in pinellas county",
    "seminole": "handyman painting pinellas county",
    "st-petersburg": "handyman services pinellas county",
    "tampa": "handyman near me small jobs",
    "town-n-country": "handyman near me small jobs",
    "westchase": "small home renovations pinellas county",
    "citrus-park": "general home repairs pinellas",
    "carrollwood": "handyman near me small jobs",
    "northdale": "handyman painting pinellas county",
    "egypt-lake-leto": "emergency handyman pinellas county",
    "temple-terrace": "carpentry services near me",
    "holiday": "plumbing services in pinellas county",
    "trinity": "handyman estimate pinellas county",
    "new-port-richey": "plumbing repair clearwater fl",
    "elfers": "handyman near me small jobs",
    "seven-springs": "carpenter pinellas county",
    "jasmine-estates": "handyman painting pinellas county",
    "beacon-square": "general home repairs pinellas",
    "port-richey": "door repair pinellas county",
    "land-o-lakes": "handyman estimate pinellas county",
}

COUNTY_PRIMARY_QUERY: dict[str, str] = {
    "pinellas": "handyman pinellas county",
    "hillsborough": "handyman near me small jobs",
    "pasco": "plumbing services in pinellas county",
}

COMBO_PRIMARY_QUERY: dict[str, str] = {
    "clearwater-sink-repair": "sink repair clearwater",
    "clearwater-drywall-repair": "plumbing repair clearwater fl",
    "safety-harbor-home-repair": "general home repairs pinellas",
    "palm-harbor-drywall-repair": "handyman pinellas county",
    "largo-toilet-repair": "plumbing services in pinellas county",
    "oldsmar-door-adjustment": "door repair pinellas county",
    "dunedin-trim-repair": "carpenter pinellas county",
    "seminole-interior-painting": "handyman painting pinellas county",
}

# Secondary terms from Serper + GSC priority export (gsc-priority-queries-2026-06-03.csv).
CITY_SECONDARY: dict[str, list[str]] = {
    "safety-harbor": ["handyman pinellas county", "handyman estimate pinellas county", "gutter installation safety harbor fl"],
    "clearwater": ["sink repair clearwater", "plumbing repair clearwater fl", "window repair clearwater"],
    "dunedin": ["handyman company pinellas", "door repair pinellas county"],
    "palm-harbor": ["handyman pinellas county fl", "general home repairs pinellas"],
    "largo": ["handyman near me small jobs", "plumbing services in pinellas county"],
    "oldsmar": ["door repair pinellas county", "handyman company pinellas"],
    "tarpon-springs": ["plumbing repair clearwater fl", "handyman pinellas county"],
    "seminole": ["handyman painting pinellas county", "interior painting pinellas"],
    "st-petersburg": ["handyman projects pinellas county", "window repair clearwater"],
    "tampa": ["handyman tampa fl", "home repair tampa bay"],
    "town-n-country": ["handyman tampa fl", "door repair hillsborough"],
    "westchase": ["handyman westchase fl", "interior painting tampa bay"],
    "citrus-park": ["handyman citrus park fl", "home repair hillsborough"],
    "carrollwood": ["handyman carrollwood fl", "pre-listing home repairs"],
    "northdale": ["handyman northdale fl", "interior painting hillsborough"],
    "egypt-lake-leto": ["landlord handyman tampa", "rental turnover repairs"],
    "temple-terrace": ["handyman temple terrace fl", "porch repair tampa"],
    "holiday": ["handyman holiday fl", "fixture plumbing pasco"],
    "trinity": ["handyman trinity fl", "pasco home repairs"],
    "new-port-richey": ["handyman new port richey fl", "riverfront home repair"],
    "elfers": ["handyman elfers fl", "affordable home repair pasco"],
    "seven-springs": ["handyman seven springs fl", "wood trim repair pasco"],
    "jasmine-estates": ["handyman jasmine estates fl", "rental patch and paint"],
    "beacon-square": ["handyman beacon square fl", "carport conversion repair"],
    "port-richey": ["handyman port richey fl", "sliding door repair gulf coast"],
    "land-o-lakes": ["handyman land o lakes fl", "new home punch list pasco"],
}

COUNTY_SECONDARY: dict[str, list[str]] = {
    "pinellas": ["handyman company pinellas", "handyman pinellas county fl", "handyman service areas pinellas county"],
    "hillsborough": ["handyman tampa bay", "handyman hillsborough county fl"],
    "pasco": ["handyman pasco county fl", "plumbing repair pasco"],
}

COMBO_SECONDARY: dict[str, list[str]] = {
    "clearwater-sink-repair": ["plumbing repair clearwater fl", "faucet repair clearwater"],
    "clearwater-drywall-repair": ["drywall repair clearwater fl", "ceiling patch clearwater"],
    "safety-harbor-home-repair": ["knight group handyman", "handyman estimate pinellas county"],
    "palm-harbor-drywall-repair": ["drywall repair palm harbor", "ceiling leak patch"],
    "largo-toilet-repair": ["toilet repair largo fl", "wax ring replacement"],
    "oldsmar-door-adjustment": ["sliding door repair pinellas", "patio door adjustment"],
    "dunedin-trim-repair": ["trim repair dunedin", "historic home carpentry"],
    "seminole-interior-painting": ["interior painting seminole fl", "stain blocking seminole"],
}


@lru_cache(maxsize=1)
def load_serp_results() -> list[dict]:
    if not SERP_JSON.is_file():
        return []
    data = json.loads(SERP_JSON.read_text(encoding="utf-8"))
    return list(data.get("results") or [])


def serp_record_for_query(query: str) -> dict | None:
    needle = query.strip().lower()
    for row in load_serp_results():
        if str(row.get("query") or "").strip().lower() == needle:
            return row
    return None


def people_also_ask(query: str, limit: int = 2) -> list[str]:
    row = serp_record_for_query(query)
    if not row:
        return []
    return [str(item).strip() for item in (row.get("people_also_ask") or []) if str(item).strip()][:limit]


def competitor_phrases(query: str, limit: int = 3) -> list[str]:
    row = serp_record_for_query(query)
    if not row:
        return []
    phrases: list[str] = []
    for comp in (row.get("top_competitors") or [])[:limit]:
        title = str(comp.get("title") or "").strip()
        if title:
            phrases.append(title)
    return phrases


def city_keywords(city_slug: str, city_name: str, county_name: str) -> dict[str, object]:
    primary = CITY_PRIMARY_QUERY.get(city_slug, f"{city_name.lower()} handyman")
    secondary = list(CITY_SECONDARY.get(city_slug, [f"handyman {county_name.lower()}"]))
    return {
        "primary": primary,
        "secondary": secondary,
        "paa": people_also_ask(primary),
        "competitors": competitor_phrases(primary),
    }


def county_keywords(county_slug: str, county_name: str) -> dict[str, object]:
    primary = COUNTY_PRIMARY_QUERY.get(county_slug, f"handyman {county_name.lower()}")
    secondary = list(COUNTY_SECONDARY.get(county_slug, []))
    return {
        "primary": primary,
        "secondary": secondary,
        "paa": people_also_ask(primary),
        "competitors": competitor_phrases(primary),
    }


def combo_keywords(combo_slug: str, city_name: str, service_label: str) -> dict[str, object]:
    primary = COMBO_PRIMARY_QUERY.get(combo_slug, f"{service_label} {city_name.lower()}")
    secondary = list(COMBO_SECONDARY.get(combo_slug, []))
    return {
        "primary": primary,
        "secondary": secondary,
        "paa": people_also_ask(primary),
        "competitors": competitor_phrases(primary),
    }
