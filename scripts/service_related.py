"""Related-service card links and trade image resolution for service/geo pages."""

from __future__ import annotations

import re
from pathlib import Path

from seo_page_data import NICHE_SERVICES, PARENT_LABELS

ROOT = Path(__file__).resolve().parents[1]
SERVICES_IMG_DIR = ROOT / "Images" / "services"
CITIES_IMG_DIR = ROOT / "Images" / "cities"

# Parent trade pages — each has a distinct card image in Images/services/
SERVICE_CARD_IMAGES: dict[str, str] = {
    "handyman": "handyman.webp",
    "general-repairs": "general-repairs.webp",
    "plumbing-services": "plumbing-services.webp",
    "electrical-work": "electrical-work.webp",
    "carpentry-framing": "carpentry-framing.webp",
    "painting-finishing": "painting-finishing.webp",
    "home-renovations": "home-renovations.webp",
    "doors-windows": "doors-windows.webp",
    "custom-projects": "custom-projects.webp",
    "emergency-services": "emergency-services.webp",
}

NICHE_PARENT: dict[str, str] = {item["slug"]: item["parent"] for item in NICHE_SERVICES}

# Default related trades shown on city/county geo pages (services only).
CORE_GEO_RELATED: list[tuple[str, str]] = [
    ("/Services/handyman", "Handyman services"),
    ("/Services/general-repairs", "General repairs"),
    ("/Services/plumbing-services", "Plumbing services"),
    ("/Services/doors-windows", "Doors & windows"),
]

# Fourth related service on combo pages when parent is already in the list above.
PARENT_NICHE_EXTRAS: dict[str, tuple[str, str]] = {
    "plumbing-services": ("/Services/faucet-replacement", "Faucet replacement"),
    "general-repairs": ("/Services/drywall-repair", "Drywall repair"),
    "handyman": ("/Services/small-jobs", "Small jobs"),
    "carpentry-framing": ("/Services/trim-repair", "Trim repair"),
    "painting-finishing": ("/Services/interior-painting", "Interior painting"),
    "doors-windows": ("/Services/door-adjustment", "Door adjustment"),
    "electrical-work": ("/Services/electrical-work", "Electrical work"),
    "home-renovations": ("/Services/custom-projects", "Custom projects"),
    "emergency-services": ("/Services/emergency-services", "Emergency services"),
    "custom-projects": ("/Services/carpentry-framing", "Carpentry & framing"),
}


def related_slug(href: str) -> str:
    return href.rstrip("/").split("/")[-1].replace(".html", "")


def _city_slug_from_geo(href_slug: str) -> str | None:
    match = re.fullmatch(r"(.+)-handyman", href_slug)
    return match.group(1) if match else None


def resolve_card_image(href: str) -> str:
    """Pick a card thumbnail for a related link (trade image; optional city override)."""
    slug = related_slug(href)

    if slug in SERVICE_CARD_IMAGES:
        filename = SERVICE_CARD_IMAGES[slug]
        if (SERVICES_IMG_DIR / filename).is_file():
            return filename

    if slug in NICHE_PARENT:
        parent = NICHE_PARENT[slug]
        filename = SERVICE_CARD_IMAGES.get(parent, "handyman.webp")
        if (SERVICES_IMG_DIR / filename).is_file():
            return filename

    city_slug = _city_slug_from_geo(slug)
    if city_slug:
        city_file = CITIES_IMG_DIR / f"{city_slug}.webp"
        if city_file.is_file():
            # Served via render_related cities branch (Images/cities/).
            return f"cities/{city_slug}.webp"

    return "handyman.webp"


def is_service_href(href: str) -> bool:
    return href.startswith("/Services/")


def geo_related_services() -> list[tuple[str, str]]:
    return list(CORE_GEO_RELATED)


def combo_related_services(parent: str, niche_slug: str, service_label: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = [
        (f"/Services/{niche_slug}", service_label.title()),
        (f"/Services/{parent}", PARENT_LABELS.get(parent, parent.replace("-", " ").title())),
    ]
    seen = {related_slug(h) for h, _ in links}
    for href, label in CORE_GEO_RELATED:
        slug = related_slug(href)
        if slug in seen:
            continue
        links.append((href, label))
        seen.add(slug)
        if len(links) >= 4:
            break
    if len(links) < 4:
        extra = PARENT_NICHE_EXTRAS.get(parent)
        if extra and related_slug(extra[0]) not in seen:
            links.append(extra)
    return links[:4]


def pricing_related_services() -> list[tuple[str, str]]:
    return [
        ("/Services/handyman", "Handyman services"),
        ("/Services/plumbing-services", "Plumbing services"),
        ("/Services/general-repairs", "General repairs"),
        ("/Services/emergency-services", "Emergency services"),
    ]


def niche_related_fallback(parent: str, slug: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = [
        (f"/Services/{parent}", PARENT_LABELS.get(parent, parent)),
    ]
    extra = PARENT_NICHE_EXTRAS.get(parent)
    if extra and related_slug(extra[0]) != slug:
        links.append(extra)
    for href, label in CORE_GEO_RELATED:
        if len(links) >= 4:
            break
        if related_slug(href) in {related_slug(h) for h, _ in links}:
            continue
        links.append((href, label))
    return links[:4]
