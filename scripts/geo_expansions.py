"""Rich HTML bodies and FAQs for city, county, and city-service geo pages."""

from __future__ import annotations

from geo_city_data import CITY_PROFILES, COMBO_PROFILES, COUNTY_PROFILES
from geo_seo_copy import city_copy, combo_copy, county_copy
from seo_page_data import COUNTY_REGIONS

GEO_FAQ: dict[str, list[tuple[str, str]]] = {}


def _jobs_list(jobs: list[str]) -> str:
    return "<ul>\n" + "\n".join(f"<li>{job}</li>" for job in jobs) + "\n</ul>"


def _county_hub_link(county_slug: str, county_name: str) -> str:
    return f'<a href="/{county_slug}-handyman">{county_name} coverage hub</a>'


def _linkify_contact(text: str) -> str:
    updated = text
    if '<a href="/booking">' not in updated:
        updated = updated.replace("booking form", '<a href="/booking">booking form</a>')
        updated = updated.replace("book online", '<a href="/booking">book online</a>')
    if "tel:" not in updated and "(813) 649-3341" in updated:
        updated = updated.replace("(813) 649-3341", '<a href="tel:+18136493341">(813) 649-3341</a>')
    return updated


def build_city_body(city_slug: str, city_name: str, county_name: str, county_slug: str) -> str:
    profile = CITY_PROFILES.get(city_slug)
    if not profile:
        return ""

    seo = city_copy(city_slug)
    county_link = _county_hub_link(county_slug, county_name)
    jobs_html = _jobs_list(profile["jobs"])
    opening = seo.get("opening") or (
        f"Knight Group provides registered, insured handyman work in {city_name}, Florida. {profile['angle']}"
    )
    scheduling = seo.get("scheduling") or (
        f"We route {county_name} from Safety Harbor. {city_name} visits receive written estimates — "
        f'<a href="/booking">book online</a> or call <a href="tel:+18136493341">(813) 649-3341</a>.'
    )
    scope_note = seo.get("scope_note") or (
        "Every job stays within handyman scope. Licensed trades are referred when permits or specialists are required."
    )
    closing_template = seo.get("closing") or (
        f"Browse {county_link}, handyman services, pricing, and our project gallery for local proof."
    )
    closing = closing_template.replace("{county_link}", county_link)

    return f"""
<h2>Handyman services in {city_name}</h2>
<p>{opening}</p>

<h3>Homes and neighborhoods we see in {city_name}</h3>
<p>{profile["housing"]} Typical service areas include {profile["areas"]}.</p>
<p>{profile["climate"]}</p>

<h3>Common {city_name} handyman requests</h3>
{jobs_html}

<h3>How scheduling works from Safety Harbor</h3>
<p>{_linkify_contact(scheduling)}</p>
<p>{scope_note}</p>

<h3>Related resources</h3>
<p>{closing}</p>
"""


def build_county_body(county_slug: str, county_name: str, city_names: list[str]) -> str:
    profile = COUNTY_PROFILES.get(county_slug)
    if not profile:
        return ""

    seo = county_copy(county_slug)
    sample = ", ".join(city_names[:6])
    if len(city_names) > 6:
        sample += f", and {len(city_names) - 6} more communities"
    themes_html = _jobs_list(profile["themes"])

    link_parts = []
    for region in COUNTY_REGIONS:
        if region["hub_slug"] == county_slug:
            for city in region["cities"][:5]:
                link_parts.append(f'<a href="/{city["slug"]}-handyman">{city["name"]}</a>')
            break
    city_links = ", ".join(link_parts)

    opening = seo.get("opening") or (
        f"Knight Group provides registered, insured handyman repairs across <strong>{county_name}</strong> from Safety Harbor."
    )
    scheduling = _linkify_contact(
        seo.get("scheduling")
        or f'Request a free written estimate through our <a href="/booking">booking form</a> with photos, or call <a href="tel:+18136493341">(813) 649-3341</a>.'
    )
    scope_note = seo.get("scope_note") or (
        "Handyman-scope repairs only. Licensed trades are referred when permits or specialists are required."
    )
    closing = seo.get("closing") or (
        'See also: <a href="/service-areas">all service areas</a>, <a href="/Services/handyman">handyman services</a>, and <a href="/pricing">pricing</a>.'
    )

    return f"""
<h2>{county_name} handyman services</h2>
<p>{opening}</p>
<p>{profile["character"]}</p>

<h3>Cities we serve in {county_name}</h3>
<p>Regular routes include {sample}. Explore city pages: {city_links}.</p>
<p>{profile["routing"]}</p>

<h3>Repair themes across {county_name}</h3>
{themes_html}

<h3>Estimates and booking</h3>
<p>{scheduling}</p>
<p>{scope_note}</p>
<p>{closing}</p>
"""


def build_combo_body(combo_slug: str, city_name: str, city_slug: str, service_label: str, niche_slug: str, county_name: str) -> str:
    profile = COMBO_PROFILES.get(combo_slug)
    if not profile:
        return ""

    seo = combo_copy(combo_slug)
    jobs_html = _jobs_list(profile["jobs"])
    city_link = f'<a href="/{city_slug}-handyman">{city_name} handyman services</a>'
    service_link = f'<a href="/Services/{niche_slug}">{service_label}</a>'
    opening = seo.get("opening") or profile["focus"]
    follow_through = seo.get("follow_through") or (
        f"When a {city_name} job touches drywall, paint, or trim after the primary repair, we sequence drying and finishing so you are not scheduling a second vendor."
    )
    booking = _linkify_contact(
        seo.get("booking")
        or f'Start at our booking form, call (813) 649-3341 for active leaks, or view {city_link} for broader repair lists in your neighborhood.'
    ).replace("booking form", '<a href="/booking">booking form</a>')

    return f"""
<h2>{service_label.title()} in {city_name}</h2>
<p>{opening}</p>
<p>{profile["focus"]}</p>

<h3>What we handle on {city_name} {service_label} visits</h3>
{jobs_html}

<h3>Handyman scope and follow-through</h3>
<p>{follow_through}</p>
<p>Read the full {service_link} page for trade-specific limits, then book a {city_name} visit with photos for accurate pricing.</p>

<h3>Book in {city_name}</h3>
<p>{booking}</p>
"""


def geo_faq_for_city(city_slug: str, city_name: str, county_name: str) -> list[tuple[str, str]]:
    key = f"{city_slug}-handyman"
    if key in GEO_FAQ:
        return GEO_FAQ[key]

    profile = CITY_PROFILES.get(city_slug, {})
    areas = profile.get("areas", county_name)
    seo = city_copy(city_slug)

    faq_price = seo.get("faq_price")
    faq_licensed = seo.get("faq_licensed")
    faq_schedule = seo.get("faq_schedule")

    return [
        (
            f"Do you provide handyman services in {city_name}?",
            f"Yes. Knight Group serves {city_name} as part of our regular {county_name} routes from Safety Harbor. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            f"Which {city_name} neighborhoods do you cover?",
            f"We work throughout {city_name} including {areas}. If you are near the city limits, mention your address when booking so we confirm the route.",
        ),
        faq_price
        if isinstance(faq_price, tuple)
        else (
            f"How do I get a written price for handyman work in {city_name}?",
            f"Use our online booking form with photos or call (813) 649-3341. Defined {city_name} scopes can often be quoted flat-rate; mixed punch lists may be hourly.",
        ),
        faq_licensed
        if isinstance(faq_licensed, tuple)
        else (
            f"Are you licensed and insured for {city_name} handyman work?",
            "Knight Group Handyman Services LLC is registered and insured in Florida. We perform handyman-scope repairs and refer licensed trades when required.",
        ),
        faq_schedule
        if isinstance(faq_schedule, tuple)
        else (
            f"How soon can you schedule a {city_name} visit?",
            f"Most standard {city_name} requests schedule within one to two business days. Active leaks or safety issues get priority when you call directly.",
        ),
    ]


def geo_faq_for_county(county_slug: str, county_name: str) -> list[tuple[str, str]]:
    key = f"{county_slug}-handyman"
    if key in GEO_FAQ:
        return GEO_FAQ[key]

    return [
        (
            f"Do you serve all of {county_name}?",
            f"Yes. Knight Group covers {county_name} on planned routes from Safety Harbor. City-specific pages list neighborhoods we visit most often — call if you are near a county line.",
        ),
        (
            f"What types of repairs do you handle in {county_name}?",
            "Drywall, fixture-level plumbing, doors, windows, painting touch-ups, carpentry, caulking, and punch-list repairs within handyman scope. We refer licensed trades for permit or repipe work.",
        ),
        (
            "How are estimates provided?",
            "Written estimates before work begins — submit photos through our booking form or call (813) 649-3341. Flat-rate when scope is defined; hourly for open-ended lists.",
        ),
        (
            "Are you insured?",
            "Knight Group Handyman Services LLC is registered and insured in Florida for handyman-scope residential repairs.",
        ),
        (
            "How soon can you schedule?",
            "Most standard requests schedule within one to two business days. Urgent leaks should be called in directly for priority routing.",
        ),
    ]


def geo_faq_for_combo(combo_slug: str, city_name: str, service_label: str) -> list[tuple[str, str]]:
    if combo_slug in GEO_FAQ:
        return GEO_FAQ[combo_slug]

    return [
        (
            f"Do you offer {service_label} in {city_name}?",
            f"Yes. Knight Group performs {service_label} in {city_name} within handyman scope. Photos help us confirm access, parts, and whether a licensed trade referral is needed.",
        ),
        (
            f"How much does {service_label} cost in {city_name}?",
            "Pricing depends on access, parts, and finish work. Defined scopes can be flat-rate after photos; complex jobs may be hourly. See our pricing hub or request a written estimate.",
        ),
        (
            "Can you handle drywall or paint after the repair?",
            "Often yes — we sequence drying and finishing so patches do not flash under paint. Mention related rooms when you book.",
        ),
        (
            "Are you licensed and insured?",
            "Knight Group is registered and insured in Florida for handyman-scope work and refers licensed trades when required.",
        ),
        (
            "How do I schedule?",
            "Book online with photos or call (813) 649-3341. Active leaks get priority routing.",
        ),
    ]


def gallery_category_for_city(city_slug: str) -> str | None:
    profile = CITY_PROFILES.get(city_slug, {})
    return profile.get("gallery_category")


def gallery_category_for_county(county_slug: str) -> str | None:
    profile = COUNTY_PROFILES.get(county_slug, {})
    return profile.get("gallery_category")
