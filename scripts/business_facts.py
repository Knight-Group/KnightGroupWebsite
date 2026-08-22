#!/usr/bin/env python3
"""Load seo/business-facts.json and emit Schema.org fragments used by generators."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FACTS_PATH = ROOT / "seo" / "business-facts.json"
BASE = "https://www.knightgroup.com"

BUSINESS_DESCRIPTION = (
    "Knight Group Handyman Services LLC provides registered and insured handyman services "
    "from Safety Harbor across Pinellas County and selected northwest Hillsborough and west Pasco routes. "
    "Recurring Home Watch and vacant-property checks remain focused on Pinellas County."
)

PINELLAS_SLUGS = {
    "safety-harbor",
    "clearwater",
    "dunedin",
    "palm-harbor",
    "largo",
    "oldsmar",
    "tarpon-springs",
    "seminole",
    "st-petersburg",
    "pinellas",
}
HILLSBOROUGH_SLUGS = {
    "tampa",
    "town-n-country",
    "westchase",
    "citrus-park",
    "carrollwood",
    "northdale",
    "egypt-lake-leto",
    "temple-terrace",
    "hillsborough",
}
PASCO_SLUGS = {
    "holiday",
    "trinity",
    "new-port-richey",
    "elfers",
    "seven-springs",
    "jasmine-estates",
    "beacon-square",
    "port-richey",
    "land-o-lakes",
    "pasco",
}


@lru_cache(maxsize=1)
def load_facts() -> dict[str, Any]:
    return json.loads(FACTS_PATH.read_text(encoding="utf-8"))


# Neighborhood labels that must stay in prose, never Schema.org City.
SCHEMA_NOT_CITIES = frozenset({"North Tampa"})


def city_nodes(names: list[str]) -> list[dict[str, str]]:
    return [
        {"@type": "City", "name": f"{name}, FL"}
        for name in names
        if name not in SCHEMA_NOT_CITIES
    ]


def county_nodes(names: list[str]) -> list[dict[str, str]]:
    return [{"@type": "AdministrativeArea", "name": f"{name}, Florida"} for name in names]


def area_from_group(group: dict[str, Any]) -> list[dict[str, str]]:
    return city_nodes(list(group.get("cities") or [])) + county_nodes(list(group.get("counties") or []))


def overall_area_served() -> list[dict[str, str]]:
    facts = load_facts()
    routes = facts["routes"]
    cities: list[str] = []
    for key in ("core", "scheduled", "expanding", "confirmFirst"):
        cities.extend(routes[key].get("cities") or [])
    seen: set[str] = set()
    unique: list[str] = []
    for city in cities:
        if city not in seen:
            seen.add(city)
            unique.append(city)
    counties = ["Pinellas County", "Hillsborough County", "Pasco County"]
    return city_nodes(unique) + county_nodes(counties)


def geography_for_url(url: str) -> list[dict[str, str]]:
    facts = load_facts()
    geo = facts["pageGeography"]
    path = url.replace(BASE, "").strip("/").lower()
    if any(token in path for token in ("home-watch", "snowbird")):
        return area_from_group(geo["homeWatch"])
    if any(slug in path for slug in sorted(PASCO_SLUGS, key=len, reverse=True)):
        return area_from_group(geo["pasco"])
    if any(slug in path for slug in sorted(HILLSBOROUGH_SLUGS, key=len, reverse=True)):
        return area_from_group(geo["hillsborough"])
    if any(slug in path for slug in sorted(PINELLAS_SLUGS, key=len, reverse=True)):
        return area_from_group(geo["pinellas"])
    return overall_area_served()


def eligible_regions(area: list[dict[str, str]]) -> list[dict[str, str]]:
    counties = [node for node in area if node.get("@type") == "AdministrativeArea"]
    if counties:
        return counties
    return area


def postal_address() -> dict[str, Any]:
    addr = load_facts()["address"]
    return {
        "@type": "PostalAddress",
        "streetAddress": addr["streetAddress"],
        "addressLocality": addr["addressLocality"],
        "addressRegion": addr["addressRegion"],
        "postalCode": addr["postalCode"],
        "addressCountry": addr["addressCountry"],
    }


def vince_id() -> str:
    return str(load_facts()["people"]["vinceKnight"]["schemaId"])


def payment_accepted() -> list[str]:
    return list(load_facts()["payments"]["accepted"])


def write_entity_json_files() -> None:
    """Keep the three public entity JSON files in lockstep with business-facts.json."""
    facts = load_facts()
    biz = facts["business"]
    vince = facts["people"]["vinceKnight"]
    seo = ROOT / "seo"

    organization = {
        "@type": "Organization",
        "@id": f"{BASE}/#organization",
        "name": biz["legalName"],
        "legalName": biz["legalName"],
        "url": biz["url"],
        "logo": f"{BASE}/Images/KnightGroupLogo.webp",
        "image": f"{BASE}/Images/KnightGroupLogo.webp",
        "email": biz["email"],
        "telephone": biz["phone"],
        "address": postal_address(),
        "founder": {"@id": vince["schemaId"]},
        "sameAs": list(facts["socialProfiles"]),
    }
    person = {
        "@type": "Person",
        "@id": vince["schemaId"],
        "name": vince["name"],
        "alternateName": vince["alternateName"],
        "jobTitle": vince["jobTitle"],
        "description": vince["description"],
        "url": vince["url"],
        "worksFor": {"@id": f"{BASE}/#organization"},
        "knowsAbout": [
            "Handyman services",
            "Plumbing-related diagnosis",
            "Drywall repair",
            "Home renovations",
            "Property maintenance",
            "Pinellas County home repair",
        ],
    }
    hours = facts["hours"]
    reviews = facts["reviews"]
    business = {
        "@type": "HomeAndConstructionBusiness",
        "@id": f"{BASE}/#business",
        "name": biz["legalName"],
        "url": biz["url"],
        "description": BUSINESS_DESCRIPTION,
        "image": [
            f"{BASE}/Images/handyman.jpg",
            f"{BASE}/Images/KGHero.webp",
        ],
        "logo": f"{BASE}/Images/KnightGroupLogo.webp",
        "telephone": biz["phone"],
        "email": biz["email"],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": biz["phone"],
                "email": biz["email"],
                "contactType": "customer service",
                "areaServed": "US-FL",
                "availableLanguage": "English",
            }
        ],
        "hasMap": facts["googleProfile"]["hasMap"],
        "parentOrganization": {"@id": f"{BASE}/#organization"},
        "founder": {"@id": vince["schemaId"]},
        "address": postal_address(),
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": facts["address"]["latitude"],
            "longitude": facts["address"]["longitude"],
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": list(hours["days"]),
                "opens": hours["opens"],
                "closes": hours["closes"],
            }
        ],
        "areaServed": overall_area_served(),
        "hasOfferCatalog": {"@id": f"{BASE}/pricing#offer-catalog"},
        "paymentAccepted": payment_accepted(),
        "currenciesAccepted": "USD",
        "foundingDate": biz["foundingDate"],
        "slogan": biz["slogan"],
        "potentialAction": {
            "@type": "ReserveAction",
            "name": "Book a free handyman estimate",
            "target": f"{BASE}/booking",
        },
        "knowsAbout": list(facts["knowsAbout"]),
        "sameAs": [*facts["socialProfiles"], facts["googleProfile"]["mapsCidUrl"]],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": reviews["ratingValue"],
            "reviewCount": reviews["reviewCount"],
            "bestRating": reviews["bestRating"],
            "worstRating": reviews["worstRating"],
        },
    }
    (seo / "knight-group-organization.json").write_text(
        json.dumps(organization, indent=2) + "\n", encoding="utf-8"
    )
    (seo / "knight-group-founder.json").write_text(
        json.dumps(person, indent=2) + "\n", encoding="utf-8"
    )
    (seo / "knight-group-business-entity.json").write_text(
        json.dumps(business, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    write_entity_json_files()
    print("Wrote organization, person, and business entity JSON from business-facts.json")
