#!/usr/bin/env python3
"""One-off generator for geo_seo_copy.py — run from scripts/."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from geo_city_data import CITY_PROFILES
from geo_serp_keywords import city_keywords, combo_keywords, county_keywords

CITIES = [
    ("safety-harbor", "Safety Harbor", "Pinellas County"),
    ("clearwater", "Clearwater", "Pinellas County"),
    ("dunedin", "Dunedin", "Pinellas County"),
    ("palm-harbor", "Palm Harbor", "Pinellas County"),
    ("largo", "Largo", "Pinellas County"),
    ("oldsmar", "Oldsmar", "Pinellas County"),
    ("tarpon-springs", "Tarpon Springs", "Pinellas County"),
    ("seminole", "Seminole", "Pinellas County"),
    ("st-petersburg", "St. Petersburg", "Pinellas County"),
    ("tampa", "Tampa", "Hillsborough County"),
    ("town-n-country", "Town 'n' Country", "Hillsborough County"),
    ("westchase", "Westchase", "Hillsborough County"),
    ("citrus-park", "Citrus Park", "Hillsborough County"),
    ("carrollwood", "Carrollwood", "Hillsborough County"),
    ("northdale", "Northdale", "Hillsborough County"),
    ("egypt-lake-leto", "Egypt Lake-Leto", "Hillsborough County"),
    ("temple-terrace", "Temple Terrace", "Hillsborough County"),
    ("holiday", "Holiday", "Pasco County"),
    ("trinity", "Trinity", "Pasco County"),
    ("new-port-richey", "New Port Richey", "Pasco County"),
    ("elfers", "Elfers", "Pasco County"),
    ("seven-springs", "Seven Springs", "Pasco County"),
    ("jasmine-estates", "Jasmine Estates", "Pasco County"),
    ("beacon-square", "Beacon Square", "Pasco County"),
    ("port-richey", "Port Richey", "Pasco County"),
    ("land-o-lakes", "Land O' Lakes", "Pasco County"),
]

OPENINGS = [
    "Knight Group Handyman Services LLC is headquartered on 7th Street South in {city} — when you search {primary}, you reach the actual local crew, not a franchise call center. {angle}",
    "Homeowners comparing {primary} options in {city} want a registered vendor who quotes before work starts. Knight Group routes {county} from Safety Harbor with journeyman-level fixture diagnosis on every visit. {angle}",
    "Looking for reliable {primary} help in {city}? Vince Knight's team handles drywall, doors, fixture plumbing, and paint-ready finishing without minimum-job games. {angle}",
    "{city} properties need a handyman who understands local housing stock — not a statewide template page. Knight Group focuses on {secondary0} and everyday punch-list work across {county}. {angle}",
    "From {areas}, Knight Group delivers {primary} service with written estimates and insured crews crossing {county} on planned routes. {angle}",
    "When {secondary0} searches spike after storm season, {city} owners call Knight Group for practical repairs that stay in handyman scope. {angle}",
    "Knight Group answers {primary} requests across {city} with photos-first estimates, flat-rate quotes on defined scopes, and hourly pricing only when punch lists are open-ended. {angle}",
    "{city} homeowners tired of national lead-gen sites choose Knight Group for {secondary0} — one Safety Harbor business, one accountable crew. {angle}",
    "Need {primary} today? Knight Group schedules {city} visits around existing {county} routes so arrival windows stay realistic and drive time does not inflate your quote. {angle}",
    "Whether you found us through {primary} or {secondary0}, Knight Group treats {city} jobs as neighborhood work — protected floors, labeled hardware, and scope explained before tools start. {angle}",
]

SCHEDULING = [
    "Dispatch runs from 1225 7th St S, Safety Harbor 34695. {city} jobs get a written estimate after photos or a quick site look — book online or call (813) 649-3341 when water is active.",
    "We batch {county} routes from our Safety Harbor shop. Share address details for {city} when booking so we confirm fit on the current week's path.",
    "{city} scheduling starts with photos through our booking form. For urgent fixture leaks, call (813) 649-3341 — we prioritize active water over standard punch lists.",
    "Estimates for {city} work are always written before tools come out. Upload pictures, list rooms affected, and we reply with flat-rate or hourly options as scope allows.",
    "Planning a {city} repair? Knight Group confirms {county} routing first, then locks an arrival window. Weekend and after-hours slots are for emergency calls only.",
]

SCOPE = [
    "Handyman scope only: we swap fixtures on existing rough-in, patch drywall, adjust doors, and finish paint-ready — no repipes, panel upgrades, or permit-level GC work.",
    "If your {city} job needs a licensed plumber, electrician, or permitted contractor, we say so on site before demolition. That honesty keeps {primary} searches from turning into change orders.",
    "Florida handyman rules matter on every {city} visit. Knight Group documents what we can legally perform and refers licensed trades when permits or specialty licenses apply.",
    "We do not perform work that requires a state license beyond handyman scope. {city} homeowners get a clear line between fixture repairs we handle and trades we coordinate out.",
    "Scope stays transparent: {secondary0} tasks we accept are quoted in writing; anything outside handyman limits is flagged before you approve labor.",
]

CLOSING = [
    "Explore our {county_link}, browse the {city} job list above, and see matching work in our project gallery. Leaks and safety issues — call, do not wait on email.",
    "Next steps: open the {county} coverage hub, review handyman services and pricing, or book with photos. Emergency water — phone first.",
    "Compare {primary} providers, then look at local proof on our gallery page. Knight Group publishes real {county} project photos, not stock interiors.",
    "Ready for a {city} quote? Visit the booking form, pricing hub, or {county_link} for neighboring communities served on the same routes.",
    "See how we handle {secondary0} on service detail pages, then schedule a {city} visit. Active leaks should be called in directly for priority routing.",
]


def clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def meta_line(name: str, primary: str) -> str:
    if name.lower() in primary.lower():
        return clip(
            f"{primary.title()}: drywall, fixture plumbing, doors and punch-list repairs. Registered and insured. Free estimate.",
            155,
        )
    return clip(
        f"{name} {primary}: drywall, fixture plumbing, doors and punch-list repairs. Registered and insured. Free estimate.",
        155,
    )


def hero_line(name: str, primary: str, areas: str) -> str:
    return clip(
        f"{primary.title()} in {name} — registered, insured Safety Harbor crew serving {areas}.",
        160,
    )


def angle_snippet(slug: str, profile: dict) -> str:
    if slug == "safety-harbor":
        return (
            "Same-day routing is easiest here, and Vince Knight knows the mix of older downtown stock "
            "and newer infill along McMullen-Booth."
        )
    return str(profile["angle"])


def main() -> None:
    lines = [
        '"""Unique SEO copy for geo pages — Serper-informed, non-duplicated across cities."""',
        "",
        "from __future__ import annotations",
        "",
        "CITY_PAGE_COPY: dict[str, dict[str, str | tuple[str, str]]] = {",
    ]

    for i, (slug, name, county) in enumerate(CITIES):
        profile = CITY_PROFILES[slug]
        kw = city_keywords(slug, name, county)
        primary = str(kw["primary"])
        secondary = list(kw["secondary"])
        sec0 = secondary[0] if secondary else f"handyman {county.lower()}"
        areas = profile["areas"].split(",")[0].strip()
        angle = angle_snippet(slug, profile)
        opening = OPENINGS[i % len(OPENINGS)].format(
            city=name, primary=primary, county=county, secondary0=sec0, areas=areas, angle=angle
        )
        scheduling = SCHEDULING[i % len(SCHEDULING)].format(city=name, county=county)
        scope_note = SCOPE[i % len(SCOPE)].format(city=name, primary=primary, secondary0=sec0)
        closing = CLOSING[i % len(CLOSING)].format(
            city=name, county=county, primary=primary, secondary0=sec0, county_link="{county_link}"
        )
        hero = hero_line(name, primary, areas)
        meta = meta_line(name, primary)
        faq_price = (
            f"How much does {primary} cost in {name}?",
            f"Pricing depends on access, parts, and finish work. Defined {name} scopes can be flat-rate after photos; open punch lists may be hourly with our published minimum visit.",
        )
        faq_licensed = (
            f"Can a handyman do plumbing or electrical work in {name}?",
            f"Knight Group performs handyman-scope fixture swaps and like-for-like replacements in {name}. Work requiring a licensed plumber, electrician, or permit is referred before tools come out.",
        )
        faq_schedule = (
            f"How fast can you reach {name} for {sec0}?",
            f"Most {name} requests schedule within one to two business days on existing {county} routes. Active leaks get priority when you call (813) 649-3341 directly.",
        )
        lines.append(f'    "{slug}": {{')
        lines.append(f'        "hero_lead": {hero!r},')
        lines.append(f'        "meta_description": {meta!r},')
        lines.append(f'        "opening": {opening!r},')
        lines.append(f'        "scheduling": {scheduling!r},')
        lines.append(f'        "scope_note": {scope_note!r},')
        lines.append(f'        "closing": {closing!r},')
        lines.append(f'        "faq_price": {faq_price!r},')
        lines.append(f'        "faq_licensed": {faq_licensed!r},')
        lines.append(f'        "faq_schedule": {faq_schedule!r},')
        lines.append("    },")

    lines.append("}")
    lines.append("")
    lines.append("COUNTY_PAGE_COPY: dict[str, dict[str, str | tuple[str, str]]] = {")

    counties = [
        ("pinellas", "Pinellas County"),
        ("hillsborough", "Hillsborough County"),
        ("pasco", "Pasco County"),
    ]
    for slug, name in counties:
        kw = county_keywords(slug, name)
        primary = str(kw["primary"])
        secondary = list(kw["secondary"])
        sec0 = secondary[0] if secondary else primary
        lines.append(f'    "{slug}": {{')
        lines.append(
            f'        "hero_lead": {clip(f"{name} handyman routes from Safety Harbor — fixture work, drywall, doors, and punch-list repairs with written estimates.", 160)!r},'
        )
        lines.append(
            f'        "meta_description": {clip(f"{primary} and {sec0}: drywall, fixture plumbing, doors. Registered and insured. Free estimate.", 155)!r},'
        )
        lines.append(
            f'        "opening": {f"Knight Group covers {name} on daily routes from Safety Harbor — search {primary} and you get a local insured crew, not a referral marketplace. We handle fixture plumbing, drywall, carpentry, painting touch-ups, and doors within handyman scope."!r},'
        )
        lines.append(
            f'        "scheduling": {f"Book {name} work with photos online or call (813) 649-3341. We confirm your city fits the current route before locking an arrival window."!r},'
        )
        lines.append(
            f'        "scope_note": {f"Handyman-scope repairs only across {name}. Licensed trades are referred when permits, repipes, or panel work are required."!r},'
        )
        lines.append(
            f'        "closing": {f"Tour city pages below, compare pricing, and view our gallery for {name} proof. Emergency leaks — call first."!r},'
        )
        lines.append("    },")

    lines.append("}")
    lines.append("")
    lines.append("COMBO_PAGE_COPY: dict[str, dict[str, str | tuple[str, str]]] = {")

    combos = [
        ("clearwater-sink-repair", "Clearwater", "sink and faucet repair"),
        ("clearwater-drywall-repair", "Clearwater", "drywall repair"),
        ("safety-harbor-home-repair", "Safety Harbor", "home repair"),
        ("palm-harbor-drywall-repair", "Palm Harbor", "drywall repair"),
        ("largo-toilet-repair", "Largo", "toilet repair"),
        ("oldsmar-door-adjustment", "Oldsmar", "door adjustment"),
        ("dunedin-trim-repair", "Dunedin", "trim repair"),
        ("seminole-interior-painting", "Seminole", "interior painting"),
    ]
    for slug, city, service in combos:
        kw = combo_keywords(slug, city, service)
        primary = str(kw["primary"])
        secondary = list(kw["secondary"])
        sec0 = secondary[0] if secondary else service
        lines.append(f'    "{slug}": {{')
        lines.append(
            f'        "hero_lead": {clip(f"{service.title()} in {city} — local Serper-targeted help, written estimates, paint-ready finish work.", 160)!r},'
        )
        lines.append(
            f'        "meta_description": {clip(f"{primary} in {city}: handyman-scope {service}. Registered and insured. Free written estimate.", 155)!r},'
        )
        lines.append(
            f'        "opening": {f"Searches for {primary} in {city} should land on a crew that knows local housing — not a generic statewide ad. Knight Group serves {city} from Safety Harbor with documented scope and {sec0} experience on real homes."!r},'
        )
        lines.append(
            f'        "follow_through": {f"After the primary {service} task, we sequence drywall, caulk, or paint so {city} homeowners are not hiring a second vendor for finish work."!r},'
        )
        lines.append(
            f'        "booking": {f"Book {city} {service} with photos, call (813) 649-3341 for active leaks, or view the city handyman page for broader repair lists."!r},'
        )
        lines.append("    },")

    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("def city_copy(slug: str) -> dict:")
    lines.append("    return dict(CITY_PAGE_COPY.get(slug, {}))")
    lines.append("")
    lines.append("")
    lines.append("def county_copy(slug: str) -> dict:")
    lines.append("    return dict(COUNTY_PAGE_COPY.get(slug, {}))")
    lines.append("")
    lines.append("")
    lines.append("def combo_copy(slug: str) -> dict:")
    lines.append("    return dict(COMBO_PAGE_COPY.get(slug, {}))")

    out = SCRIPT_DIR / "geo_seo_copy.py"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
