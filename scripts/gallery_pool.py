#!/usr/bin/env python3
"""Validated GalleryImages .webp pool for inline service/city page galleries."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "GalleryImages"
CITIES_IMG_DIR = ROOT / "Images" / "cities"
MANIFEST_PATH = GALLERY_DIR / "gallery-manifest.json"

SERVICE_PARENT_TO_CATEGORY = {
    "plumbing-services": "plumbing",
    "carpentry-framing": "carpentry",
    "general-repairs": "general-repairs",
    "painting-finishing": "painting",
    "doors-windows": "carpentry",
    "home-renovations": "renovations",
    "handyman": "general-repairs",
    "electrical-work": "electrical",
    "emergency-services": "general-repairs",
    "custom-projects": "general-repairs",
}

# Curated inline gallery images for pages that must not use category hash picks.
SLUG_GALLERY_OVERRIDES: dict[str, list[dict[str, str]]] = {
    "electrical-work": [
        {
            "src": "GalleryImages/fixtures-fans-02.webp",
            "alt": "Ceiling fan installed on existing connection — electrical work in Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-04.webp",
            "alt": "Light fixture installed — electrical work in Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-05.webp",
            "alt": "Light fixture installation completed — electrical work in Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-01.webp",
            "alt": "Ceiling junction prepped for fixture or fan install — electrical work in Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-06.webp",
            "alt": "Electrical box ready for fixture swap — Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-07.webp",
            "alt": "Ceiling connection point for fan or fixture — electrical work Pinellas County FL by Knight Group",
            "category": "electrical",
        },
        {
            "src": "GalleryImages/fixtures-fans-03.webp",
            "alt": "Light fixture mounting location prepared — electrical work in Pinellas County FL by Knight Group",
            "category": "electrical",
        },
    ],
}

_POOL: list[dict[str, str]] | None = None


def _webp_exists(filename: str) -> bool:
    return (GALLERY_DIR / filename).is_file()


def load_gallery_pool() -> list[dict[str, str]]:
    global _POOL
    if _POOL is not None:
        return _POOL

    items: list[dict[str, str]] = []
    seen: set[str] = set()

    if MANIFEST_PATH.is_file():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for group in manifest.get("groups", []):
            category = group.get("category") or "general-repairs"
            for img in group.get("images") or []:
                src = str(img.get("src") or "")
                if not src.endswith(".webp"):
                    continue
                filename = src.rsplit("/", 1)[-1]
                if filename in seen or not _webp_exists(filename):
                    continue
                seen.add(filename)
                items.append(
                    {
                        "src": f"GalleryImages/{filename}",
                        "alt": str(
                            img.get("seoAlt")
                            or img.get("title")
                            or group.get("title")
                            or "Knight Group handyman project photo in Pinellas County FL"
                        ),
                        "category": category,
                    }
                )

    for path in sorted(GALLERY_DIR.glob("*.webp")):
        rel = f"GalleryImages/{path.name}"
        if path.name in seen:
            continue
        seen.add(path.name)
        items.append(
            {
                "src": rel,
                "alt": "Knight Group handyman project photo in Pinellas County FL",
                "category": "general-repairs",
            }
        )

    _POOL = items
    return _POOL


def pick_gallery_images(
    slug: str,
    count: int = 4,
    category: str | None = None,
) -> list[dict[str, str]]:
    override = SLUG_GALLERY_OVERRIDES.get(slug)
    if override:
        valid = _validated_images(override)
        if valid:
            if len(valid) <= count:
                return valid[:count]
            start = int(hashlib.sha256(slug.encode("utf-8")).hexdigest(), 16) % len(valid)
            return [valid[(start + offset) % len(valid)] for offset in range(count)]

    pool = load_gallery_pool()
    if not pool:
        return []

    filtered = [item for item in pool if category is None or item["category"] == category]
    if len(filtered) < count:
        filtered = pool
    if len(filtered) <= count:
        return filtered[:count]

    start = int(hashlib.sha256(slug.encode("utf-8")).hexdigest(), 16) % len(filtered)
    return [filtered[(start + offset) % len(filtered)] for offset in range(count)]


def _city_image_exists(filename: str) -> bool:
    return (CITIES_IMG_DIR / filename).is_file()


def _image_exists(src_rel: str) -> bool:
    if src_rel.startswith("Images/cities/"):
        return _city_image_exists(src_rel.rsplit("/", 1)[-1])
    filename = src_rel.rsplit("/", 1)[-1]
    return _webp_exists(filename)


def _validated_images(images: list[dict[str, str]]) -> list[dict[str, str]]:
    valid: list[dict[str, str]] = []
    for image in images:
        src_rel = str(image.get("src") or "")
        if src_rel and _image_exists(src_rel):
            valid.append(image)
    return valid


def _heading_insert_positions(prose: str, count: int) -> list[int]:
    ends = [match.end() for match in re.finditer(r"</h[23]>", prose, re.I)]
    if not ends:
        paragraph_end = prose.lower().find("</p>")
        if paragraph_end != -1:
            return [paragraph_end + 4]
        return []

    if count >= len(ends):
        return ends[:count]

    positions: list[int] = []
    for index in range(count):
        slot = round((index + 0.5) * len(ends) / count - 0.5)
        slot = max(0, min(len(ends) - 1, slot))
        positions.append(ends[slot])
    return positions


def _localize_gallery_alt(alt: str, county_name: str, city_name: str) -> str:
    if not county_name:
        return alt
    localized = alt.replace("Pinellas County FL", f"{county_name} FL")
    localized = localized.replace("Pinellas County", county_name)
    if city_name and "handyman project photo" in localized.lower():
        localized = f"{city_name} handyman project photo in {county_name} FL by Knight Group"
    return localized


def pick_geo_gallery_images(
    page_slug: str,
    *,
    city_slug: str | None = None,
    county_slug: str | None = None,
    city_name: str = "",
    county_name: str = "",
    count: int = 4,
    category: str | None = None,
) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    area_slug = city_slug or county_slug
    if area_slug:
        city_file = f"{area_slug}.webp"
        if _city_image_exists(city_file):
            try:
                from city_landmark_catalog import landmark_alt

                label = city_name or area_slug.replace("-", " ").title()
                alt = landmark_alt(area_slug, label, county=bool(county_slug and not city_slug))
            except ImportError:
                label = city_name or area_slug.replace("-", " ").title()
                alt = f"{label}, Florida — Knight Group handyman service area"
            images.append(
                {
                    "src": f"Images/cities/{city_file}",
                    "alt": alt,
                    "category": "geo",
                }
            )

    remaining = max(0, count - len(images))
    if remaining:
        for item in pick_gallery_images(page_slug, count=remaining, category=category):
            localized = dict(item)
            localized["alt"] = _localize_gallery_alt(
                str(item.get("alt") or ""),
                county_name,
                city_name,
            )
            images.append(localized)
    return images[:count]


def render_inline_figure(
    image: dict[str, str],
    prefix: str,
    align: str,
    alt_fallback: str = "",
    cache_bust: str = "",
) -> str:
    src_rel = str(image.get("src") or "")
    filename = src_rel.rsplit("/", 1)[-1]
    if not filename or not _image_exists(src_rel):
        return ""

    alt = html.escape(image.get("alt") or alt_fallback, quote=True)
    align = "left" if align == "left" else "right"
    version = f"?v={cache_bust}" if cache_bust else ""
    if src_rel.startswith("Images/cities/"):
        src = f"{prefix}{src_rel}{version}"
    else:
        src = f"{prefix}GalleryImages/{filename}{version}"
    return (
        f'\n<figure class="kg-prose-photo kg-prose-photo--{align}">'
        f'<img src="{src}" alt="{alt}" width="480" height="360" loading="lazy" decoding="async">'
        f"</figure>\n"
    )


def embed_images_in_prose(
    prose: str,
    images: list[dict[str, str]],
    prefix: str,
    alt_fallback: str = "",
    *,
    max_images: int = 4,
    cache_bust: str = "",
) -> str:
    if not prose.strip():
        return prose

    valid = _validated_images(images)
    if not valid:
        return prose

    image_count = min(max_images, len(valid), 3 if prose.count("</h2>") + prose.count("</h3>") < 4 else 4)
    positions = _heading_insert_positions(prose, image_count)
    if not positions:
        return prose

    image_count = min(image_count, len(positions))
    inserts: list[tuple[int, str]] = []
    for index in range(image_count):
        align = "right" if index % 2 == 0 else "left"
        figure = render_inline_figure(valid[index], prefix, align, alt_fallback, cache_bust)
        if figure:
            inserts.append((positions[index], figure))

    updated = prose
    for position, figure in sorted(inserts, key=lambda item: item[0], reverse=True):
        updated = updated[:position] + figure + updated[position:]
    return updated


def prose_with_inline_gallery(
    prose: str,
    slug: str,
    prefix: str,
    *,
    count: int = 4,
    category: str | None = None,
    alt_fallback: str = "",
    city_slug: str | None = None,
    county_slug: str | None = None,
    city_name: str = "",
    county_name: str = "",
    cache_bust: str = "",
) -> str:
    if city_slug or county_slug:
        images = pick_geo_gallery_images(
            slug,
            city_slug=city_slug,
            county_slug=county_slug,
            city_name=city_name,
            county_name=county_name,
            count=count,
            category=category,
        )
    else:
        images = pick_gallery_images(slug, count=count, category=category)
    return embed_images_in_prose(
        prose,
        images,
        prefix,
        alt_fallback,
        cache_bust=cache_bust,
    )


def render_gallery_html(
    images: list[dict[str, str]],
    prefix: str,
    alt_fallback: str = "",
) -> str:
    cards = []
    for image in images:
        src_rel = str(image.get("src") or "")
        filename = src_rel.rsplit("/", 1)[-1]
        if not filename or not _webp_exists(filename):
            continue
        alt = html.escape(image.get("alt") or alt_fallback, quote=True)
        src = f"{prefix}GalleryImages/{filename}"
        cards.append(
            f"""                        <figure class="kg-service-gallery__item">
                            <img src="{src}" alt="{alt}" width="640" height="480" loading="lazy" decoding="async">
                        </figure>"""
        )
        if len(cards) >= 4:
            break

    if not cards:
        return ""

    return f"""
            <section class="kg-section kg-service-gallery-wrap" aria-label="Project photos">
                <div class="kg-shell">
                    <div class="kg-service-gallery-grid">
{chr(10).join(cards)}
                    </div>
                </div>
            </section>"""
