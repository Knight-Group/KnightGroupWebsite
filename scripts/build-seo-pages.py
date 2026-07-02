#!/usr/bin/env python3
"""Generate SEO expansion pages and page-manifest.json from seo_page_data definitions."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_detail_copy import gallery_body_extra, gallery_meta  # noqa: E402
from gallery_pool import (  # noqa: E402
    SERVICE_PARENT_TO_CATEGORY,
    prose_with_inline_gallery,
)
from geo_expansions import (  # noqa: E402
    build_city_body,
    build_combo_body,
    build_county_body,
    gallery_category_for_city,
    gallery_category_for_county,
    geo_faq_for_city,
    geo_faq_for_combo,
    geo_faq_for_county,
)
from geo_seo_copy import city_copy, combo_copy, county_copy  # noqa: E402
from service_sidebar import render_service_sidebar  # noqa: E402
from schema_graph import build_graph_for_page, service_by_slug  # noqa: E402
from page_meta import clip_title, resolve_description, social_tags  # noqa: E402
from niche_detail import NICHE_BOOKING, NICHE_DETAIL, NICHE_LOCAL  # noqa: E402
from page_copy_helpers import cta_lead, faq_intro, scope_disclaimer_html  # noqa: E402
from niche_expansions import NICHE_BODY, NICHE_FAQ, NICHE_RELATED  # noqa: E402
from service_related import (  # noqa: E402
    combo_related_services,
    geo_related_services,
    niche_related_fallback,
    pricing_related_services,
    resolve_card_image,
)
from seo_page_data import (  # noqa: E402
    CITIES,
    CITY_COMBOS,
    COUNTY_REGIONS,
    NICHE_SERVICES,
    PARENT_LABELS,
    PRICING_PAGES,
    TRUST_PAGES,
)
from trust_content import build_trust_prose, trust_faqs, trust_related_links  # noqa: E402

ROOT = SCRIPT_DIR.parent
SEO = ROOT / "seo"
VERSION = "20260701-seo-audit-fix"
BASE = "https://www.knightgroup.com"

GALLERY_PICKS = [
    "bathroom-tub-window-remodel",
    "blinds-replacement-before-after",
    "bathroom-remodel-cobblestone",
    "garbage-disposal-install",
    "mold-wall-repair",
    "pipe-repair-before-after",
    "floor-subfloor-repair",
    "tub-drain-replacement",
]


def esc(value: str) -> str:
    return html.escape(value.strip(), quote=True)


def path_prefix(output: Path) -> str:
    rel = output.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth if depth else ""


def default_faqs(topic: str, city: str = "Pinellas County") -> list[tuple[str, str]]:
    return [
        (
            f"Do you offer {topic} in {city}?",
            f"Yes. Knight Group serves homeowners across {city} with registered, insured handyman-scope work. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            "How do I get a price before work starts?",
            "Request a free written estimate online or call (813) 649-3341. For defined small scopes we can often quote a flat rate; mixed punch lists may be hourly depending on access and materials.",
        ),
        (
            "Are you registered and insured?",
            "Knight Group Handyman Services LLC is registered and insured in Florida. We perform handyman-scope repairs and refer licensed trades when a permit or specialist is required.",
        ),
        (
            "How soon can you schedule?",
            "Most standard requests schedule within one to two business days. Active leaks or urgent safety issues get priority when you call directly.",
        ),
        (
            "What should I prepare before your visit?",
            "Clear access to the work area, note any prior repairs, and list parts you already purchased. Photos through the booking form help us bring the right tools on the first trip.",
        ),
    ]


def render_faq(
    items: list[tuple[str, str]],
    slug: str,
    county_name: str = "Pinellas County",
    *,
    h1: str = "",
    intro: str | None = None,
) -> str:
    rows = []
    for question, answer in items:
        rows.append(
            f"""                        <details class="kg-faq-item">
                            <summary>{esc(question)}</summary>
                            <p>{esc(answer)}</p>
                        </details>"""
        )
    intro_text = intro or faq_intro(slug, h1 or slug.replace("-", " "), county_name)
    return f"""
            <section class="kg-section kg-service-faq" id="{slug}-faq" aria-labelledby="{slug}-faq-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">FAQ</span>
                        <h2 id="{slug}-faq-heading">Frequently asked questions</h2>
                        <p>{esc(intro_text)}</p>
                    </div>
                    <div class="kg-faq-list">
{chr(10).join(rows)}
                    </div>
            </section>"""


def render_related(links: list[tuple[str, str]], prefix: str) -> str:
    cards = []
    text_links = []
    for href, label in links:
        if href.startswith("/Services/"):
            image = resolve_card_image(href)
            if image.startswith("cities/"):
                img_src = f"/Images/{image}"
            else:
                img_src = f"/Images/services/{image}"
            cards.append(
                f"""                        <a class="kg-service-related-card" href="{href}">
                            <img src="{img_src}?v={VERSION}" alt="{esc(label)}" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">{esc(label)}</span>
                        </a>"""
            )
        else:
            text_links.append(f'                        <a class="kg-service-related-card kg-service-related-card--text" href="{href}">{esc(label)}</a>')
    if not cards and not text_links:
        return ""
    text_block = "\n".join(text_links)
    card_block = "\n".join(cards)
    combined = "\n".join(part for part in (card_block, text_block) if part)
    return f"""
            <section class="kg-section kg-service-related" aria-labelledby="related-services-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">Related services</span>
                        <h2 id="related-services-heading">Other services we offer</h2>
                    </div>
                    <div class="kg-service-related-grid">
{combined}
                    </div>
            </section>"""


def prose_block(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)


def build_niche_prose(defn: dict) -> str:
    slug = defn["slug"]
    h1 = defn["h1"].rstrip(".")
    lead = defn["lead"]
    detail = NICHE_DETAIL.get(slug, "").strip()
    body = NICHE_BODY.get(slug, "").strip()
    local = NICHE_LOCAL.get(slug, "").strip()
    booking = NICHE_BOOKING.get(slug, "").strip()
    if not body and not detail:
        parent = PARENT_LABELS.get(defn["parent"], defn["parent"])
        body = prose_block(
            [
                f"Knight Group handles {h1.lower()} across Safety Harbor, Clearwater, and Pinellas County as part of our {parent.lower()} work.",
                "Request a free written estimate with photos before work begins.",
            ]
        )
    parts = [f"<h2>{esc(h1)}</h2>", f"<p>{esc(lead)}</p>"]
    if detail:
        parts.append(detail)
    if body:
        parts.append(body)
    if local:
        parts.append(local)
    if booking:
        parts.append(booking)
    return "\n".join(parts)


def build_city_prose(city_slug: str, city_name: str, county_name: str, county_slug: str) -> str:
    body = build_city_body(city_slug, city_name, county_name, county_slug).strip()
    if body:
        return body
    return prose_block(
        [
            f"Knight Group provides local handyman services in {city_name}, Florida.",
            "Request a free estimate online or call (813) 649-3341.",
        ]
    )


def build_county_prose(county_slug: str, county_name: str, city_names: list[str]) -> str:
    body = build_county_body(county_slug, county_name, city_names).strip()
    if body:
        return body
    sample = ", ".join(city_names[:5])
    return prose_block(
        [
            f"Knight Group provides registered, insured handyman services across {county_name}, Florida.",
            f"We serve homeowners throughout {county_name}, including {sample}.",
        ]
    )


def build_combo_prose(
    combo_slug: str,
    city_slug: str,
    city_name: str,
    service_label: str,
    niche_slug: str,
    county_name: str,
) -> str:
    body = build_combo_body(combo_slug, city_name, city_slug, service_label, niche_slug, county_name).strip()
    if body:
        return body
    return prose_block(
        [
            f"Looking for {service_label} in {city_name}? Knight Group handles focused repair scopes for local homeowners.",
            f"See our dedicated {service_label} page for scope details, then book a {city_name} visit with photos.",
        ]
    )


def county_for_city(city_slug: str) -> tuple[str, str]:
    for region in COUNTY_REGIONS:
        for city in region["cities"]:
            if city["slug"] == city_slug:
                return region["hub_slug"], region["hub_name"]
    return "pinellas", "Pinellas County"


def build_pricing_prose(defn: dict) -> str:
    slug = defn.get("slug", "")
    if slug == "pricing-no-2-hour-minimum":
        return prose_block(
            [
                defn["lead"],
                "Many Tampa Bay handyman franchises bill a two-hour minimum even when the repair takes forty-five minutes. Knight Group bills hourly from $75–$150 depending on the work type, with <strong>no 2-hour minimum</strong> — you pay for actual time on site.",
                "That matters for small jobs: a single faucet swap, door adjustment, shelf install, or caulk refresh should not cost the same as a half-day block. Punch lists and mixed small tasks are a strong fit for this model.",
                "For defined scopes with known parts and finish, we still offer written flat-rate quotes after photos or a short visit. See <a href=\"/pricing\">full pricing</a> and <a href=\"/pricing-handyman-by-the-hour\">hourly handyman rates</a> for comparison.",
                "Request a free written estimate online or call (813) 649-3341 to describe your list and confirm fit before we schedule.",
            ]
        )
    return prose_block(
        [
            defn["lead"],
            "Knight Group publishes clear pricing philosophy: defined small scopes can be quoted flat-rate after photos or a short site visit, while mixed punch lists and diagnostic work are often billed hourly with a minimum visit.",
            "Hourly handyman work covers multiple small tasks in one trip — hardware installs, adjustments, caulking, and minor repairs that share setup time. Flat-rate quotes work best when the scope, parts, and finish are known upfront.",
            "Plumbing fixture pricing stays within handyman scope: swaps and minor leak corrections using existing rough-in, not repipes or permit work. Electrical fixture swaps follow the same pattern for like-for-like replacements.",
            "Every estimate is written before work begins. Request a quote online or call (813) 649-3341 to discuss your list and which pricing model fits best.",
        ]
    )


def vince_cutout_hero_wrap() -> str:
    return f"""
            <div class="kg-page-hero__cutout-wrap" aria-hidden="true" data-kg-enter="right">
                <picture>
                    <source srcset="/Images/knight-hero-cutout.webp?v={VERSION}" type="image/webp">
                    <img class="kg-page-hero-cutout" src="/Images/knight-hero-cutout.png" alt="Vince Knight, owner of Knight Group Handyman Services" width="1200" height="800" decoding="async" loading="eager">
                </picture>
            </div>"""


def page_shell(
    *,
    output: Path,
    title: str,
    description: str,
    canonical: str,
    breadcrumb: list[tuple[str, str]],
    h1: str,
    lead: str,
    hero_image: str,
    body_html: str,
    faq_html: str,
    related_html: str,
    json_ld: dict,
    scope: bool = False,
    eyebrow: str = "Safety Harbor · Pinellas County",
    sidebar_lead: str = "Free written estimates across Pinellas County.",
    sidebar_label: str = "service",
    sidebar_county: str = "Pinellas County",
    cta_lead_text: str | None = None,
) -> str:
    prefix = path_prefix(output)
    slug = output.stem
    crumbs = []
    for href, label in breadcrumb:
        if href:
            crumbs.append(f'<a href="{href}">{esc(label)}</a><span aria-hidden="true">/</span>')
        else:
            crumbs.append(f'<span aria-current="page">{esc(label)}</span>')
    scope_block = scope_disclaimer_html(slug) if scope else ""
    cta_text = cta_lead_text or cta_lead(slug, h1, sidebar_county)
    graph_json = json.dumps(json_ld, indent=4, ensure_ascii=False)
    cutout_wrap = vince_cutout_hero_wrap()
    sidebar_html = render_service_sidebar(slug, sidebar_label, sidebar_lead, sidebar_county)
    og_html = social_tags(title=title, description=description, canonical=canonical)

    return f"""<!DOCTYPE html>
<html lang="en" class="kg-js">
<head>
    <script>window.dataLayer = window.dataLayer || [];</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="/JS/canonical-redirect.js"></script>
    <link rel="icon" type="image/png" sizes="32x32" href="/Images/favicon-32x32.png">
    <link rel="apple-touch-icon" href="/Images/apple-touch-icon.png">
    <meta name="theme-color" content="#9a2f2f">
    <meta name="author" content="Knight Group Handyman Services LLC">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
{og_html}
    <script type="application/ld+json">
{graph_json}
    </script>
    <link rel="stylesheet" href="/CSS/header.min.css?v={VERSION}">
    <link rel="stylesheet" href="/CSS/kg-redesign.css?v={VERSION}">
    <script src="/JS/kg-redesign.js?v={VERSION}" defer></script>
</head>
<body class="kg-page kg-service">
    <div id="header-include"></div>
    <main id="main-content">
        <section class="kg-page-hero kg-service-hero" aria-labelledby="{slug}-hero-heading">
{cutout_wrap}
            <div class="kg-shell kg-page-hero__grid">
                <div class="kg-page-hero__copy">
                    <nav class="kg-breadcrumb" aria-label="Breadcrumb">
                        {''.join(crumbs)}
                    </nav>
                    <span class="kg-eyebrow">{esc(eyebrow)}</span>
                    <h1 id="{slug}-hero-heading">{esc(h1)}</h1>
                    <p class="kg-page-hero__lead">{esc(lead)}</p>
                </div>
            </div>
        </section>
        <div class="kg-service-stack">
            <div class="kg-shell kg-service-layout">
                <div class="kg-service-main">
            <section class="kg-section kg-service-detail">
                        <div class="kg-service-prose">
                            {scope_block}
                            {body_html}
                        </div>
            </section>
            {faq_html}
            {related_html}
            <section class="kg-section kg-service-cta">
                    <div class="kg-heading-block">
                        <h2>Ready to schedule?</h2>
                        <p>{esc(cta_text)}</p>
                    </div>
                    <div class="kg-service-cta__actions">
                        <a href="/booking" class="kg-btn kg-btn--solid">Book a free estimate</a>
                        <a href="/pricing" class="kg-btn kg-btn--ghost">View pricing</a>
                    </div>
            </section>
                </div>
{sidebar_html}
            </div>
        </div>
    </main>
    <div id="footer-include"></div>
    <script src="/JS/includes.min.js?v={VERSION}" defer></script>
</body>
</html>
"""


def faq_entities(items: list[tuple[str, str]]) -> list[dict]:
    return [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in items
    ]


def write_page(output: Path, html_text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_text, encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)}")


def manifest_entry(page_type: str, slug: str, path: str, canonical: str, priority: str = "0.75") -> dict:
    return {
        "pageType": page_type,
        "slug": slug,
        "path": path,
        "canonical": canonical,
        "priority": priority,
    }


def generate_niche(defn: dict, manifest: list) -> None:
    slug = defn["slug"]
    output = ROOT / "Services" / f"{slug}.html"
    rel_path = f"Services/{slug}.html"
    canonical = f"{BASE}/Services/{slug}"
    description = resolve_description(rel_path, defn["lead"])
    parent_label = PARENT_LABELS.get(defn["parent"], defn["parent"])
    faqs = NICHE_FAQ.get(slug) or default_faqs(defn["h1"].lower())
    try:
        service = service_by_slug(defn["parent"])
    except KeyError:
        service = {
            "slug": slug,
            "name": defn["h1"],
            "serviceType": defn["h1"],
            "description": description,
            "image": defn["hero"].replace(".webp", ".jpg"),
        }
    service = dict(service)
    service["name"] = defn["h1"]
    service["description"] = description
    meta = {"title": defn["title"], "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="service-detail",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = NICHE_RELATED.get(slug) or niche_related_fallback(defn["parent"], slug)
    html_text = page_shell(
        output=output,
        title=clip_title(defn["title"]),
        description=description,
        canonical=canonical,
        breadcrumb=[
            ("/", "Home"),
            ("/services", "Services"),
            (f"/Services/{defn['parent']}", parent_label),
            ("", defn["h1"].title() if defn["h1"].islower() else defn["h1"]),
        ],
        h1=defn["h1"],
        lead=defn["lead"],
        hero_image=defn["hero"],
        body_html=prose_with_inline_gallery(
            build_niche_prose(defn),
            slug,
            path_prefix(output),
            category=SERVICE_PARENT_TO_CATEGORY.get(defn["parent"]),
            alt_fallback=defn["h1"],
        ),
        faq_html=render_faq(faqs, slug, h1=defn["h1"]),
        related_html=render_related(related, path_prefix(output)),
        json_ld=graph,
        scope=bool(defn.get("scope")),
        sidebar_label=defn["h1"],
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("niche-service", slug, f"Services/{slug}.html", canonical, "0.78"))


def generate_city(
    city_slug: str,
    city_name: str,
    county_name: str,
    county_slug: str,
    manifest: list,
    *,
    expand: bool = False,
    seo_primary: bool = False,
) -> None:
    slug = f"{city_slug}-handyman"
    output = ROOT / f"{slug}.html"
    canonical = f"{BASE}/{slug}"
    seo = city_copy(city_slug)
    title_name = "Town n Country" if city_slug == "town-n-country" else city_name
    title = clip_title(f"{title_name} Handyman | {county_name} | Knight Group")
    lead = str(seo.get("hero_lead") or f"Local handyman repairs, fixtures, and punch-list work for {city_name} homeowners.")
    description = resolve_description(
        f"{slug}.html",
        str(
            seo.get("meta_description")
            or f"{city_name} handyman for drywall, plumbing fixtures, doors, and home repairs. Registered and insured. Free estimate."
        ),
    )
    faqs = geo_faq_for_city(city_slug, city_name, county_name)
    service = {
        "name": f"{city_name} handyman services",
        "serviceType": f"Handyman services in {city_name}",
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="geo-city",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = geo_related_services()
    priority = "0.82" if expand or seo_primary else "0.78"
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/service-areas", "Service Areas"), ("", city_name)],
        h1=f"{city_name} handyman services",
        lead=lead,
        hero_image="handyman.webp",
        body_html=prose_with_inline_gallery(
            build_city_prose(city_slug, city_name, county_name, county_slug),
            slug,
            "",
            city_slug=city_slug,
            city_name=city_name,
            county_name=county_name,
            category=gallery_category_for_city(city_slug),
            alt_fallback=f"{city_name} handyman project in {county_name}",
            cache_bust=VERSION,
        ),
        faq_html=render_faq(faqs, slug, county_name, h1=f"{city_name} handyman services"),
        related_html=render_related(related, ""),
        json_ld=graph,
        eyebrow=f"Safety Harbor · {county_name}",
        sidebar_lead=f"Free written estimates across {county_name} and nearby Tampa Bay communities.",
        sidebar_label=f"{city_name} handyman",
        sidebar_county=county_name,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("city", slug, f"{slug}.html", canonical, priority))


def generate_county_hub(region: dict, manifest: list) -> None:
    hub_slug = region["hub_slug"]
    county_name = region["hub_name"]
    slug = f"{hub_slug}-handyman"
    output = ROOT / f"{slug}.html"
    canonical = f"{BASE}/{slug}"
    seo = county_copy(hub_slug)
    title = clip_title(f"{county_name} Handyman | Knight Group")
    lead = str(
        seo.get("hero_lead")
        or f"{county_name} handyman repairs, fixtures, drywall, doors, and punch-list work from a registered Safety Harbor team."
    )
    description = resolve_description(
        f"{slug}.html",
        str(
            seo.get("meta_description")
            or f"{county_name} handyman for drywall, plumbing fixtures, doors, and home repairs. Registered and insured. Free estimate."
        ),
    )
    city_names = [city["name"] for city in region["cities"]]
    faqs = geo_faq_for_county(hub_slug, county_name)
    service = {
        "name": f"{county_name} handyman services",
        "serviceType": f"Handyman services in {county_name}",
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="geo-county",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = geo_related_services()
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/service-areas", "Service Areas"), ("", county_name)],
        h1=f"{county_name} handyman services",
        lead=lead,
        hero_image="handyman.webp",
        body_html=prose_with_inline_gallery(
            build_county_prose(hub_slug, county_name, city_names),
            slug,
            "",
            county_slug=hub_slug,
            city_name=county_name,
            county_name=county_name,
            category=gallery_category_for_county(hub_slug),
            alt_fallback=f"{county_name} handyman project",
            cache_bust=VERSION,
        ),
        faq_html=render_faq(faqs, slug, county_name, h1=f"{county_name} handyman services"),
        related_html=render_related(related, ""),
        json_ld=graph,
        eyebrow=f"Safety Harbor · {county_name}",
        sidebar_lead=f"Free written estimates across {county_name} and nearby Tampa Bay communities.",
        sidebar_label=f"{county_name} handyman",
        sidebar_county=county_name,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("county", slug, f"{slug}.html", canonical, "0.84"))


def generate_pricing(defn: dict, manifest: list) -> None:
    slug = defn["slug"].replace("pricing-", "")
    filename = f"pricing-{slug}.html"
    output = ROOT / filename
    canonical = f"{BASE}/{filename.replace('.html', '')}"
    description = resolve_description(filename, defn["lead"])
    faqs = default_faqs(defn["h1"].lower())
    service = {
        "name": defn["h1"],
        "serviceType": defn["h1"],
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": defn["title"], "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="pricing-niche",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = pricing_related_services()
    html_text = page_shell(
        output=output,
        title=clip_title(defn["title"]),
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/pricing", "Pricing"), ("", defn["h1"])],
        h1=defn["h1"],
        lead=defn["lead"],
        hero_image="handyman.webp",
        body_html=build_pricing_prose(defn),
        faq_html=render_faq(faqs, slug, h1=defn["h1"]),
        related_html=render_related(related, ""),
        json_ld=graph,
        sidebar_label=defn["h1"],
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("pricing-niche", slug, filename, canonical, "0.76"))


def generate_trust(defn: dict, manifest: list) -> None:
    slug = defn["slug"]
    filename = f"{slug}.html"
    output = ROOT / filename
    rel_path = filename
    canonical = f"{BASE}/{slug}"
    description = resolve_description(rel_path, defn["lead"])
    faqs = trust_faqs(slug) or default_faqs(defn["h1"].lower())
    service = {
        "name": defn["h1"],
        "serviceType": defn["h1"],
        "description": description,
        "image": defn.get("hero", "handyman.webp"),
    }
    meta = {"title": clip_title(defn["title"]), "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="service-detail",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = trust_related_links(slug)
    html_text = page_shell(
        output=output,
        title=clip_title(defn["title"]),
        description=description,
        canonical=canonical,
        breadcrumb=defn.get("breadcrumb") or [("/", "Home"), ("", defn["h1"])],
        h1=defn["h1"],
        lead=defn["lead"],
        hero_image=defn.get("hero", "handyman.webp"),
        body_html=build_trust_prose(defn),
        faq_html=render_faq(faqs, slug, h1=defn["h1"]),
        related_html=render_related(related, ""),
        json_ld=graph,
        sidebar_label=defn["h1"],
        eyebrow="Registered · Insured · Pinellas County",
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("trust-guide", slug, filename, canonical, "0.74"))


def generate_combo(city_slug: str, service_slug: str, city_name: str, service_label: str, parent: str, niche_slug: str, manifest: list) -> None:
    slug = f"{city_slug}-{service_slug}"
    output = ROOT / f"{slug}.html"
    canonical = f"{BASE}/{slug}"
    seo = combo_copy(slug)
    title = clip_title(f"{service_label.title()} in {city_name} | Knight Group")
    lead = str(
        seo.get("hero_lead")
        or f"{service_label.title()} for {city_name} homes — one local handyman team, written estimates, and neat finish work."
    )
    _, county_name = county_for_city(city_slug)
    description = resolve_description(
        f"{slug}.html",
        str(
            seo.get("meta_description")
            or f"{service_label} in {city_name}, {county_name}. Handyman-scope repairs. Free estimate."
        ),
    )
    faqs = geo_faq_for_combo(slug, city_name, service_label)
    service = {
        "name": f"{service_label} in {city_name}",
        "serviceType": service_label,
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="geo-combo",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = combo_related_services(parent, niche_slug, service_label)
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/service-areas", "Service Areas"), (f"/{city_slug}-handyman", city_name), ("", service_label.title())],
        h1=f"{service_label} in {city_name}",
        lead=lead,
        hero_image=f"{parent}.webp" if (ROOT / "Images" / "services" / f"{parent}.webp").exists() else "handyman.webp",
        body_html=prose_with_inline_gallery(
            build_combo_prose(slug, city_slug, city_name, service_label, niche_slug, county_name),
            slug,
            "",
            city_slug=city_slug,
            city_name=city_name,
            county_name=county_name,
            category=SERVICE_PARENT_TO_CATEGORY.get(parent),
            alt_fallback=f"{city_name} {service_label} in {county_name}",
            cache_bust=VERSION,
        ),
        faq_html=render_faq(faqs, slug, county_name, h1=f"{service_label} in {city_name}"),
        related_html=render_related(related, ""),
        json_ld=graph,
        scope=parent == "plumbing-services",
        sidebar_label=f"{service_label} in {city_name}",
        sidebar_county=county_name,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("city-service", slug, f"{slug}.html", canonical, "0.77"))


def generate_gallery_project(group: dict, manifest: list) -> None:
    slug = group["id"]
    output = ROOT / "gallery" / f"{slug}.html"
    rel_path = f"gallery/{slug}.html"
    canonical = f"{BASE}/gallery/{slug}"
    title = clip_title(f"{group['title']} | Knight Group")
    description = resolve_description(rel_path, gallery_meta(slug, group["description"]))
    images = group.get("images") or []
    img_html = ""
    prefix = "../"
    for img in images[:6]:
        src = img["src"]
        filename = src.rsplit("/", 1)[-1]
        if not filename.endswith(".webp") or not (ROOT / "GalleryImages" / filename).is_file():
            continue
        img_src = src if src.startswith("/") else f"/{src.lstrip('/')}"
        img_html += f'<figure><img src="{img_src}" alt="{esc(img.get("seoAlt", group["title"]))}" loading="lazy" width="800" height="600"></figure>'
    extra = gallery_body_extra(slug)
    body = prose_block(
        [
            group["description"],
            "This project is representative of handyman and renovation work Knight Group performs across Pinellas County. Scope, materials, and timeline are confirmed in writing before work begins.",
            "Want similar work at your property? Book a free estimate with photos of your space.",
        ]
    )
    if extra:
        body = body + extra
    faqs = default_faqs(group["title"].lower())
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(page_key="gallery-project", meta=meta, faq_entities=faq_entities(faqs))
    related = [
        ("/galleries", "All gallery projects"),
        (group.get("serviceLink", "/services"), "Related service"),
        ("/booking", "Book estimate"),
    ]
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/galleries", "Gallery"), ("", group["title"])],
        h1=group["title"],
        lead=group["description"],
        hero_image="home-renovations.webp",
        body_html=body + f'<div class="kg-gallery-project-images">{img_html}</div>',
        faq_html=render_faq(faqs, slug, h1=group["title"]),
        related_html=render_related(related, prefix),
        json_ld=graph,
        sidebar_label=group["title"],
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("gallery-project", slug, f"gallery/{slug}.html", canonical, "0.62"))


def build_manifest() -> list[dict]:
    manifest: list[dict] = []
    for defn in NICHE_SERVICES:
        generate_niche(defn, manifest)
    for region in COUNTY_REGIONS:
        generate_county_hub(region, manifest)
        for city in region["cities"]:
            expand = city["slug"] in {"clearwater", "safety-harbor", "tampa", "new-port-richey"}
            generate_city(
                city["slug"],
                city["name"],
                region["hub_name"],
                region["hub_slug"],
                manifest,
                expand=expand,
                seo_primary=bool(city.get("seo_primary")),
            )
    for defn in PRICING_PAGES:
        generate_pricing(defn, manifest)
    for defn in TRUST_PAGES:
        generate_trust(defn, manifest)
    for city_slug, service_slug, city_name, service_label, parent, niche_slug in CITY_COMBOS:
        generate_combo(city_slug, service_slug, city_name, service_label, parent, niche_slug, manifest)
    extra_combos = [
        ("palm-harbor", "drywall-repair", "Palm Harbor", "drywall repair", "general-repairs", "drywall-repair"),
        ("largo", "toilet-repair", "Largo", "toilet repair", "plumbing-services", "toilet-repair"),
        ("oldsmar", "door-adjustment", "Oldsmar", "door adjustment", "doors-windows", "door-adjustment"),
        ("dunedin", "trim-repair", "Dunedin", "trim repair", "carpentry-framing", "trim-repair"),
        ("seminole", "interior-painting", "Seminole", "interior painting", "painting-finishing", "interior-painting"),
    ]
    for args in extra_combos:
        generate_combo(*args, manifest)
    manifest_data = json.loads((ROOT / "GalleryImages" / "gallery-manifest.json").read_text(encoding="utf-8"))
    groups_by_id = {g["id"]: g for g in manifest_data.get("groups", [])}
    for pick in GALLERY_PICKS:
        group = groups_by_id.get(pick)
        if group:
            generate_gallery_project(group, manifest)
    return manifest


def main() -> int:
    manifest = build_manifest()
    (SEO / "page-manifest.json").write_text(
        json.dumps({"generated": True, "version": VERSION, "pages": manifest}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(manifest)} pages to manifest.")
    import subprocess
    import sys

    subprocess.run([sys.executable, str(ROOT / "scripts" / "encode-asset-paths.py")], check=True)
    from audit_gallery_refs import main as audit_gallery_refs
    from audit_image_refs import main as audit_image_refs

    if audit_gallery_refs() != 0:
        print("Gallery audit failed.", file=sys.stderr)
        return 1
    if audit_image_refs() != 0:
        print("Image ref audit failed.", file=sys.stderr)
        return 1
    print("Gallery audit passed.")
    print("Image ref audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
