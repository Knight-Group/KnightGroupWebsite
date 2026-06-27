"""City/county landmark image catalog — Wikipedia lead photos + alt text."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_JSON = ROOT / "data" / "wiki_landmark_urls.json"

# Fallback labels when JSON is missing an entry.
LANDMARK_LABELS: dict[str, str] = {
    "clearwater": "Clearwater Beach on the Gulf of Mexico",
    "tampa": "Downtown Tampa skyline along the Hillsborough River",
    "st-petersburg": "St. Pete Pier and downtown St. Petersburg waterfront",
    "dunedin": "Dunedin downtown and the Pinellas Gulf shoreline",
    "tarpon-springs": "Dodecanese Avenue and the Tarpon Springs sponge docks",
    "safety-harbor": "City of Safety Harbor official seal",
    "largo": "Largo Public Library in central Largo",
    "palm-harbor": "Ozona waterfront sunset near Palm Harbor",
    "seminole": "Seminole and the Lake Seminole area",
    "oldsmar": "Oldsmar City Hall and downtown Oldsmar",
    "land-o-lakes": "Land O' Lakes communities in Pasco County",
    "new-port-richey": "City of New Port Richey entrance and downtown corner",
    "holiday": "Holiday and the Pasco County Gulf Coast",
    "port-richey": "Port Richey waterfront on the Pithlachascotee River",
    "temple-terrace": "Temple Terrace and the Hillsborough River oak canopy",
    "town-n-country": "Town 'n' Country in Hillsborough County near Tampa Bay",
    "westchase": "Westchase planned community in northwest Hillsborough",
    "citrus-park": "Citrus Park and northwest Tampa suburbs",
    "carrollwood": "Carrollwood in northwest Hillsborough County",
    "northdale": "Northdale near Carrollwood and Citrus Park",
    "egypt-lake-leto": "Egypt Lake-Leto west of downtown Tampa",
    "trinity": "Trinity planned community in Pasco County",
    "elfers": "Elfers in west Pasco County",
    "seven-springs": "Seven Springs and wooded Pasco County",
    "jasmine-estates": "Jasmine Estates in Pasco County",
    "beacon-square": "Beacon Square near Holiday and New Port Richey",
    "pinellas": "Pinellas County Gulf beaches and coastline",
    "hillsborough": "Hillsborough County — downtown Tampa skyline",
    "pasco": "Pasco County Gulf Coast and river communities",
}


def load_wiki_catalog() -> dict[str, dict]:
    if not WIKI_JSON.is_file():
        return {}
    return json.loads(WIKI_JSON.read_text(encoding="utf-8"))


def get_city_landmark(slug: str) -> dict[str, str] | None:
    entry = load_wiki_catalog().get(slug)
    if not entry or not entry.get("url"):
        return None
    return {
        "url": entry["url"],
        "landmark": entry.get("landmark") or LANDMARK_LABELS.get(slug, slug),
    }


def landmark_alt(slug: str, city_name: str, *, county: bool = False) -> str:
    entry = get_city_landmark(slug)
    landmark = (entry or {}).get("landmark") or LANDMARK_LABELS.get(slug) or city_name
    return f"{landmark} — Knight Group handyman service area"
