#!/usr/bin/env python3
"""Re-embed curated before/process/after media on service, city, combo, and trust pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_pool import prose_with_inline_gallery  # noqa: E402
from seo_page_data import CITY_COMBOS, COUNTY_REGIONS, TRUST_PAGES  # noqa: E402

ROOT = SCRIPT_DIR.parent
SERVICES = ROOT / "Services"
CSS_VERSION = "20260825-media-roles"
CACHE_BUST = "20260825-media"
SKIP_SERVICES = {
    "index",
    "programming&databases",
    "handcraftedfurniture&resins",
}

PROSE_BLOCK = re.compile(
    r'(<div class="kg-service-prose">\s*)(.*?)(\s*</div>\s*<(?:aside class="kg-service-sidebar"|/section))',
    re.S,
)
FIGURE = re.compile(r"\s*<figure class=\"kg-prose-photo.*?</figure>\s*", re.S)
STYLESHEET = re.compile(r'(href="(?:\.\./)?CSS/kg-redesign\.css)\?v=[^"]+"')

EXTRA_COMBOS = [
    ("palm-harbor", "drywall-repair", "Palm Harbor"),
    ("largo", "toilet-repair", "Largo"),
    ("oldsmar", "door-adjustment", "Oldsmar"),
    ("dunedin", "trim-repair", "Dunedin"),
    ("seminole", "interior-painting", "Seminole"),
]


def clean_prose(prose: str) -> str:
    prose = FIGURE.sub("\n", prose)
    prose = re.sub(r"(<h[1-6][^>]*>)\s*\?\?\s*", r"\1", prose)
    prose = re.sub(r"\?\?\s*Safety First", "Safety First", prose)
    prose = re.sub(r"\ufffd+", "", prose)
    prose = re.sub(r'<div class="warning-box">', '<div class="kg-service-callout">', prose)
    return prose.strip()


def county_for_city(city_slug: str) -> tuple[str, str]:
    for region in COUNTY_REGIONS:
        for city in region["cities"]:
            if city["slug"] == city_slug:
                return region["hub_slug"], region["hub_name"]
    return "", ""


def bump_stylesheet(html: str) -> str:
    return STYLESHEET.sub(rf'\1?v={CSS_VERSION}"', html)


def refresh_page(
    path: Path,
    slug: str,
    *,
    city_slug: str | None = None,
    county_slug: str | None = None,
    city_name: str = "",
    county_name: str = "",
    prefix: str = "",
) -> bool:
    if not path.is_file():
        print(f"skip missing: {path.name}")
        return False

    html = path.read_text(encoding="utf-8")
    match = PROSE_BLOCK.search(html)
    if not match:
        print(f"skip no prose: {path.name}")
        return False

    prose = clean_prose(match.group(2))
    prose = prose_with_inline_gallery(
        prose,
        slug,
        prefix,
        city_slug=city_slug,
        county_slug=county_slug,
        city_name=city_name,
        county_name=county_name,
        alt_fallback=f"{slug.replace('-', ' ')} project photo",
        cache_bust=CACHE_BUST,
    )
    updated = html[: match.start(2)] + "\n" + prose + "\n                        " + html[match.end(2) :]
    updated = bump_stylesheet(updated)
    path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"refreshed gallery: {path.relative_to(ROOT)}")
    return True


def iter_targets() -> list[tuple]:
    targets: list[tuple] = []
    for path in sorted(SERVICES.glob("*.html")):
        if path.stem in SKIP_SERVICES:
            continue
        targets.append((path, path.stem, {"prefix": "../"}))

    for region in COUNTY_REGIONS:
        county_slug = region["hub_slug"]
        county_name = region["hub_name"]
        targets.append(
            (
                ROOT / f"{county_slug}-handyman.html",
                f"{county_slug}-handyman",
                {"county_slug": county_slug, "county_name": county_name},
            )
        )
        for city in region["cities"]:
            targets.append(
                (
                    ROOT / f"{city['slug']}-handyman.html",
                    f"{city['slug']}-handyman",
                    {
                        "city_slug": city["slug"],
                        "city_name": city["name"],
                        "county_name": county_name,
                    },
                )
            )

    combos = [(row[0], row[1], row[2]) for row in CITY_COMBOS] + EXTRA_COMBOS
    for city_slug, service_slug, city_name in combos:
        _, county_name = county_for_city(city_slug)
        slug = f"{city_slug}-{service_slug}"
        targets.append(
            (
                ROOT / f"{slug}.html",
                slug,
                {
                    "city_slug": city_slug,
                    "city_name": city_name,
                    "county_name": county_name,
                },
            )
        )

    for defn in TRUST_PAGES:
        targets.append((ROOT / f"{defn['slug']}.html", defn["slug"], {}))

    return targets


def main() -> int:
    refreshed = 0
    for path, slug, kwargs in iter_targets():
        if refresh_page(path, slug, **kwargs):
            refreshed += 1
    print(f"refreshed {refreshed} pages")
    from audit_gallery_refs import main as audit_gallery_refs

    return audit_gallery_refs()


if __name__ == "__main__":
    raise SystemExit(main())
