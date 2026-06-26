#!/usr/bin/env python3
"""Fetch Wikipedia lead images for geo cities (slow — avoids 429)."""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data" / "wiki_landmark_urls.json"

WIKI_TITLES = {
    "clearwater": "Clearwater,_Florida",
    "tampa": "Tampa,_Florida",
    "st-petersburg": "St._Petersburg,_Florida",
    "dunedin": "Dunedin,_Florida",
    "tarpon-springs": "Tarpon_Springs,_Florida",
    "safety-harbor": "Safety_Harbor,_Florida",
    "largo": "Largo,_Florida",
    "palm-harbor": "Palm_Harbor,_Florida",
    "seminole": "Seminole,_Florida",
    "oldsmar": "Oldsmar,_Florida",
    "land-o-lakes": "Land_O%27_Lakes,_Florida",
    "new-port-richey": "New_Port_Richey,_Florida",
    "holiday": "Holiday,_Florida",
    "port-richey": "Port_Richey,_Florida",
    "temple-terrace": "Temple_Terrace,_Florida",
    "town-n-country": "Town_%27n%27_Country,_Florida",
    "westchase": "Westchase,_Florida",
    "citrus-park": "Citrus_Park,_Florida",
    "carrollwood": "Carrollwood,_Florida",
    "northdale": "Northdale,_Florida",
    "egypt-lake-leto": "Egypt_Lake-Leto,_Florida",
    "trinity": "Trinity,_Florida",
    "elfers": "Elfers,_Florida",
    "seven-springs": "Seven_Springs,_Florida",
    "jasmine-estates": "Jasmine_Estates,_Florida",
    "beacon-square": "Beacon_Square,_Florida",
    "pinellas": "Pinellas_County,_Florida",
    "hillsborough": "Hillsborough_County,_Florida",
    "pasco": "Pasco_County,_Florida",
}

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


def fetch_summary(title: str) -> dict:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    req = urllib.request.Request(url, headers={"User-Agent": "KnightGroupWebsite/1.0 (landmark fetch)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def upscale_thumb(thumb: str) -> str:
    if not thumb:
        return thumb
    for size in ("330px-", "320px-", "440px-", "500px-"):
        if f"/{size}" in thumb:
            return thumb.replace(f"/{size}", "/1280px-")
    return thumb


def main() -> int:
    existing: dict[str, dict] = {}
    if OUT_JSON.is_file():
        existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    out = dict(existing)
    failures = 0
    for slug, title in WIKI_TITLES.items():
        if slug in out and out[slug].get("url"):
            continue
        try:
            data = fetch_summary(title)
            thumb = upscale_thumb((data.get("thumbnail") or {}).get("source", ""))
            if not thumb:
                raise RuntimeError("no lead image on Wikipedia")
            out[slug] = {
                "url": thumb,
                "landmark": LANDMARK_LABELS.get(slug, data.get("title", slug)),
                "title": data.get("title", ""),
                "source": "wikipedia",
            }
            print(f"OK {slug}")
        except Exception as exc:
            failures += 1
            print(f"FAIL {slug}: {exc}")
        time.sleep(2.5)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {OUT_JSON} ({len(out)} entries, {failures} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
