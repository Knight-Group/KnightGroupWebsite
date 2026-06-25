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

from schema_graph import build_graph_for_page, service_by_slug  # noqa: E402
from seo_page_data import (  # noqa: E402
    CITIES,
    CITY_COMBOS,
    NICHE_SERVICES,
    PARENT_LABELS,
    PRICING_PAGES,
    SCOPE_DISCLAIMER,
)

ROOT = SCRIPT_DIR.parent
SEO = ROOT / "seo"
VERSION = "20260622-seo"
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

GALLERY_IMAGES = [
    "GalleryImages/Refinished Bathroom_Window.webp",
    "GalleryImages/before-after-broken-blinds-replaced.webp",
    "GalleryImages/general-repairs.webp",
    "GalleryImages/plumbing-services.webp",
    "GalleryImages/carpentry-framing.webp",
    "GalleryImages/doors-windows.webp",
    "GalleryImages/painting-finishing.webp",
    "GalleryImages/handyman.webp",
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
            "Are you licensed and insured?",
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


def render_faq(items: list[tuple[str, str]], slug: str) -> str:
    rows = []
    for question, answer in items:
        rows.append(
            f"""                        <details class="kg-faq-item">
                            <summary>{esc(question)}</summary>
                            <p>{esc(answer)}</p>
                        </details>"""
        )
    return f"""
            <section class="kg-section kg-service-faq" id="{slug}-faq" aria-labelledby="{slug}-faq-heading">
                <div class="kg-shell">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">FAQ</span>
                        <h2 id="{slug}-faq-heading">Frequently asked questions</h2>
                    </div>
                    <div class="kg-faq-list">
{chr(10).join(rows)}
                    </div>
                </div>
            </section>"""


def render_gallery(images: list[str], prefix: str, alt_base: str) -> str:
    cards = []
    for src in images[:4]:
        cards.append(
            f"""                        <figure class="kg-service-gallery__item">
                            <img src="{prefix}{src}" alt="{esc(alt_base)}" width="640" height="480" loading="lazy" decoding="async">
                        </figure>"""
        )
    return f"""
            <section class="kg-section kg-service-gallery-wrap" aria-label="Project photos">
                <div class="kg-shell">
                    <div class="kg-service-gallery-grid">
{chr(10).join(cards)}
                    </div>
                </div>
            </section>"""


def render_related(links: list[tuple[str, str]], prefix: str) -> str:
    cards = []
    for href, label in links:
        cards.append(
            f"""                        <a class="kg-service-related-card" href="{href}">
                            <span class="kg-service-related-card__label">{esc(label)}</span>
                        </a>"""
        )
    return f"""
            <section class="kg-section kg-service-related" aria-labelledby="related-services-heading">
                <div class="kg-shell">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">Related</span>
                        <h2 id="related-services-heading">Related pages</h2>
                    </div>
                    <div class="kg-service-related-grid">
{chr(10).join(cards)}
                    </div>
                </div>
            </section>"""


def prose_block(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)


def build_niche_prose(defn: dict) -> str:
    parent = PARENT_LABELS.get(defn["parent"], defn["parent"])
    topic = defn["h1"].rstrip(".")
    return prose_block(
        [
            defn["lead"],
            f"Homeowners across Safety Harbor, Clearwater, and Pinellas County call Knight Group when they want one accountable team instead of chasing separate vendors. We handle {topic.lower()} as part of our broader {parent.lower()} work, with journeyman-level fixture experience on the handyman scope.",
            "Every visit starts with confirming access, materials, and whether the repair fits handyman scope or needs a licensed trade referral. You get a written estimate before work begins, and we protect finished surfaces while work is in progress.",
            "Typical jobs include prep and cleanup, hardware and consumables on smaller scopes, and coordination when drywall, paint, or carpentry must follow the primary repair. If you are comparing hourly vs flat-rate pricing, see our pricing pages or request a quote with photos for a defined scope.",
            "Ready to schedule? Book online, call (813) 649-3341, or send a message with photos. We respond quickly during business hours and prioritize active leaks or safety issues when you call directly.",
        ]
    )


def build_city_prose(city_slug: str, city_name: str) -> str:
    return prose_block(
        [
            f"Knight Group provides local handyman services in {city_name}, Florida — drywall, fixtures, doors, painting touch-ups, and punch-list repairs for homeowners and small landlords.",
            f"From older Pinellas block homes to newer townhomes, {city_name} properties see humidity-related caulking failures, fixture wear, and small water events that need fast, neat corrections. We schedule most standard requests within one to two business days.",
            f"Our team is based in Safety Harbor and works across Pinellas County daily, so {city_name} is a core service area rather than an occasional trip. You get the same registered, insured crew whether the job is one faucet or a mixed repair list.",
            "Common requests include sink and toilet fixture work, drywall patches after leaks, door adjustments, trim repair, interior paint touch-ups, and rental turn punch lists. We confirm scope on site and provide written pricing before starting.",
            "Request a free estimate online or call (813) 649-3341 with a short description and photos. We will confirm fit, timeline, and whether any portion requires a licensed trade referral.",
        ]
    )


def build_combo_prose(city_name: str, service_label: str, niche_slug: str) -> str:
    return prose_block(
        [
            f"Looking for {service_label} in {city_name}? Knight Group handles focused repair scopes for local homeowners without treating your job like a generic statewide landing page.",
            f"We combine {service_label} with related drywall, paint, or carpentry follow-through when needed so you are not juggling multiple vendors for one bathroom or laundry issue.",
            f"{city_name} homes often need quick fixture corrections after tenant turnover, seasonal humidity damage, or aging supply lines. We document the scope, protect finished surfaces, and leave work areas broom-clean.",
            f"See our dedicated {service_label} page for scope details, then book a {city_name} visit with photos for accurate pricing. Active leaks should be called in directly at (813) 649-3341.",
        ]
    )


def build_pricing_prose(defn: dict) -> str:
    return prose_block(
        [
            defn["lead"],
            "Knight Group publishes clear pricing philosophy: defined small scopes can be quoted flat-rate after photos or a short site visit, while mixed punch lists and diagnostic work are often billed hourly with a minimum visit.",
            "Hourly handyman work covers multiple small tasks in one trip — hardware installs, adjustments, caulking, and minor repairs that share setup time. Flat-rate quotes work best when the scope, parts, and finish are known upfront.",
            "Plumbing fixture pricing stays within handyman scope: swaps and minor leak corrections using existing rough-in, not repipes or permit work. Electrical fixture swaps follow the same pattern for like-for-like replacements.",
            "Every estimate is written before work begins. Request a quote online or call (813) 649-3341 to discuss your list and which pricing model fits best.",
        ]
    )


def hero_image_block(hero_file: str, prefix: str, label: str) -> str:
    return f"""
                <div class="kg-page-hero__media" data-kg-enter="right">
                    <picture>
                        <source srcset="{prefix}Images/services/{hero_file}?v={VERSION}" type="image/webp">
                        <img src="{prefix}Images/services/{hero_file.replace('.webp', '.jpg')}" alt="{esc(label)} project photo in Pinellas County" width="640" height="480" loading="eager" decoding="async">
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
    gallery_html: str,
    json_ld: dict,
    scope: bool = False,
) -> str:
    prefix = path_prefix(output)
    slug = output.stem
    crumbs = []
    for href, label in breadcrumb:
        if href:
            crumbs.append(f'<a href="{href}">{esc(label)}</a><span aria-hidden="true">/</span>')
        else:
            crumbs.append(f'<span aria-current="page">{esc(label)}</span>')
    scope_block = SCOPE_DISCLAIMER if scope else ""
    graph_json = json.dumps(json_ld, indent=4, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en" class="kg-js">
<head>
    <script>window.dataLayer = window.dataLayer || [];</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="{prefix}JS/canonical-redirect.js"></script>
    <link rel="icon" type="image/png" sizes="32x32" href="{prefix}Images/favicon-32x32.png">
    <link rel="apple-touch-icon" href="/Images/apple-touch-icon.png">
    <meta name="theme-color" content="#9a2f2f">
    <meta name="author" content="Knight Group Handyman Services LLC">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <script type="application/ld+json">
{graph_json}
    </script>
    <link rel="stylesheet" href="{prefix}CSS/header.min.css?v={VERSION}">
    <link rel="stylesheet" href="{prefix}CSS/kg-redesign.css?v={VERSION}">
    <script src="{prefix}JS/kg-redesign.js?v={VERSION}" defer></script>
</head>
<body class="kg-page kg-service">
    <div id="header-include"></div>
    <main id="main-content">
        <section class="kg-page-hero kg-service-hero" aria-labelledby="{slug}-hero-heading">
            <div class="kg-shell kg-page-hero__grid">
                <div class="kg-page-hero__copy">
                    <nav class="kg-breadcrumb" aria-label="Breadcrumb">
                        {''.join(crumbs)}
                    </nav>
                    <span class="kg-eyebrow">Safety Harbor · Pinellas County</span>
                    <h1 id="{slug}-hero-heading">{esc(h1)}</h1>
                    <p class="kg-page-hero__lead">{esc(lead)}</p>
                </div>
{hero_image_block(hero_image, prefix, h1)}
            </div>
        </section>
        <div class="kg-service-stack">
            <section class="kg-section kg-service-detail">
                <div class="kg-shell">
                    <div class="kg-service-layout">
                        <div class="kg-service-prose">
                            {scope_block}
                            {body_html}
                        </div>
                        <aside class="kg-service-sidebar" aria-label="Book service">
                            <h3>Book service</h3>
                            <p class="kg-service-sidebar__lead">Free written estimates across Pinellas County.</p>
                            <div class="kg-service-sidebar__actions">
                                <a href="/booking" class="kg-btn kg-btn--solid">Request free estimate</a>
                                <a href="tel:+18136493341" class="kg-btn kg-btn--ghost">Call (813) 649-3341</a>
                            </div>
                        </aside>
                    </div>
                </div>
            </section>
            {gallery_html}
            {faq_html}
            {related_html}
            <section class="kg-section kg-service-cta">
                <div class="kg-shell">
                    <div class="kg-heading-block">
                        <h2>Ready to schedule?</h2>
                        <p>Tell us what needs attention and where the property is located.</p>
                    </div>
                    <div class="kg-service-cta__actions">
                        <a href="/booking" class="kg-btn kg-btn--solid">Book a free estimate</a>
                        <a href="/pricing" class="kg-btn kg-btn--ghost">View pricing</a>
                    </div>
                </div>
            </section>
        </div>
    </main>
    <div id="footer-include"></div>
    <script src="{prefix}JS/includes.min.js?v={VERSION}" defer></script>
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
    canonical = f"{BASE}/Services/{slug}"
    description = defn["lead"][:155]
    parent_label = PARENT_LABELS.get(defn["parent"], defn["parent"])
    faqs = default_faqs(defn["h1"].lower())
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
    related = [
        (f"/Services/{defn['parent']}", parent_label),
        ("/pricing", "Pricing"),
        ("/clearwater-handyman", "Clearwater handyman"),
        (f"/Services/drywall-repair", "Drywall repair"),
    ]
    html_text = page_shell(
        output=output,
        title=defn["title"],
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/services", "Services"), ("", parent_label)],
        h1=defn["h1"],
        lead=defn["lead"],
        hero_image=defn["hero"],
        body_html=build_niche_prose(defn),
        faq_html=render_faq(faqs, slug),
        related_html=render_related(related, path_prefix(output)),
        gallery_html=render_gallery(GALLERY_IMAGES[:3], path_prefix(output), defn["h1"]),
        json_ld=graph,
        scope=bool(defn.get("scope")),
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("niche-service", slug, f"Services/{slug}.html", canonical, "0.78"))


def generate_city(city_slug: str, city_name: str, manifest: list, expand: bool = False) -> None:
    slug = f"{city_slug}-handyman"
    output = ROOT / f"{slug}.html"
    canonical = f"{BASE}/{slug}"
    title = f"{city_name} Handyman Services | Pinellas County FL | Knight Group"
    lead = f"Local handyman repairs, fixtures, and punch-list work for {city_name} homeowners."
    description = f"{city_name} handyman for drywall, plumbing fixtures, doors, and home repairs. Registered & insured. Free estimate."
    faqs = default_faqs("handyman services", city_name)
    service = {
        "name": f"{city_name} handyman services",
        "serviceType": f"Handyman services in {city_name}",
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="geo-handyman",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = [
        ("/service-areas", "Service areas"),
        ("/pinellas-handyman", "Pinellas County"),
        ("/Services/handyman", "Handyman services"),
        ("/pricing", "Pricing"),
    ]
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/service-areas", "Service Areas"), ("", city_name)],
        h1=f"{city_name} handyman services",
        lead=lead,
        hero_image="handyman.webp",
        body_html=build_city_prose(city_slug, city_name),
        faq_html=render_faq(faqs, slug),
        related_html=render_related(related, ""),
        gallery_html=render_gallery(GALLERY_IMAGES[1:5], "", f"{city_name} handyman"),
        json_ld=graph,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("city", slug, f"{slug}.html", canonical, "0.82" if expand else "0.80"))


def generate_pricing(defn: dict, manifest: list) -> None:
    slug = defn["slug"].replace("pricing-", "")
    filename = f"pricing-{slug}.html"
    output = ROOT / filename
    canonical = f"{BASE}/{filename.replace('.html', '')}"
    description = defn["lead"][:155]
    faqs = default_faqs(defn["h1"].lower())
    service = {
        "name": defn["h1"],
        "serviceType": defn["h1"],
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": defn["title"], "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="pricing",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = [("/pricing", "Pricing overview"), ("/Services/handyman", "Handyman"), ("/booking", "Book estimate")]
    html_text = page_shell(
        output=output,
        title=defn["title"],
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/pricing", "Pricing"), ("", defn["h1"])],
        h1=defn["h1"],
        lead=defn["lead"],
        hero_image="handyman.webp",
        body_html=build_pricing_prose(defn),
        faq_html=render_faq(faqs, slug),
        related_html=render_related(related, ""),
        gallery_html="",
        json_ld=graph,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("pricing-niche", slug, filename, canonical, "0.76"))


def generate_combo(city_slug: str, service_slug: str, city_name: str, service_label: str, parent: str, niche_slug: str, manifest: list) -> None:
    slug = f"{city_slug}-{service_slug}"
    output = ROOT / f"{slug}.html"
    canonical = f"{BASE}/{slug}"
    title = f"{service_label.title()} in {city_name} FL | Knight Group"
    lead = f"{service_label.title()} for {city_name} homes — one local handyman team, written estimates, and neat finish work."
    description = f"{service_label} in {city_name}, Pinellas County. Handyman-scope repairs. Free estimate."
    faqs = default_faqs(service_label, city_name)
    service = {
        "name": f"{service_label} in {city_name}",
        "serviceType": service_label,
        "description": description,
        "image": "handyman.jpg",
    }
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(
        page_key="geo-handyman",
        meta=meta,
        faq_entities=faq_entities(faqs),
        service=service,
    )
    related = [
        (f"/{city_slug}-handyman", f"{city_name} handyman"),
        (f"/Services/{niche_slug}", service_label.title()),
        (f"/Services/{parent}", PARENT_LABELS.get(parent, parent)),
        ("/pricing", "Pricing"),
    ]
    html_text = page_shell(
        output=output,
        title=title,
        description=description,
        canonical=canonical,
        breadcrumb=[("/", "Home"), ("/service-areas", "Service Areas"), (f"/{city_slug}-handyman", city_name), ("", service_label.title())],
        h1=f"{service_label} in {city_name}",
        lead=lead,
        hero_image=f"{parent}.webp" if (ROOT / "Images" / "services" / f"{parent}.webp").exists() else "handyman.webp",
        body_html=build_combo_prose(city_name, service_label, niche_slug),
        faq_html=render_faq(faqs, slug),
        related_html=render_related(related, ""),
        gallery_html=render_gallery(GALLERY_IMAGES[2:6], "", f"{city_name} {service_label}"),
        json_ld=graph,
        scope=parent == "plumbing-services",
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("city-service", slug, f"{slug}.html", canonical, "0.77"))


def generate_gallery_project(group: dict, manifest: list) -> None:
    slug = group["id"]
    output = ROOT / "gallery" / f"{slug}.html"
    canonical = f"{BASE}/gallery/{slug}"
    title = f"{group['title']} | Knight Group Gallery"
    description = group["description"][:155]
    images = group.get("images") or []
    img_html = ""
    prefix = "../"
    for img in images[:6]:
        src = img["src"].replace("GalleryImages/", "GalleryImages/")
        img_html += f'<figure><img src="{prefix}{src}" alt="{esc(img.get("seoAlt", group["title"]))}" loading="lazy" width="800" height="600"></figure>'
    body = prose_block(
        [
            group["description"],
            "This project is representative of handyman and renovation work Knight Group performs across Pinellas County. Scope, materials, and timeline are confirmed in writing before work begins.",
            "Want similar work at your property? Book a free estimate with photos of your space.",
        ]
    )
    faqs = default_faqs(group["title"].lower())
    meta = {"title": title, "description": description, "canonical": canonical}
    graph = build_graph_for_page(page_key="galleries", meta=meta, faq_entities=faq_entities(faqs))
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
        faq_html=render_faq(faqs, slug),
        related_html=render_related(related, prefix),
        gallery_html="",
        json_ld=graph,
    )
    write_page(output, html_text)
    manifest.append(manifest_entry("gallery-project", slug, f"gallery/{slug}.html", canonical, "0.62"))


def build_manifest() -> list[dict]:
    manifest: list[dict] = []
    for defn in NICHE_SERVICES:
        generate_niche(defn, manifest)
    for city_slug, city_name in CITIES:
        expand = city_slug in {"clearwater", "safety-harbor"}
        generate_city(city_slug, city_name, manifest, expand=expand)
    generate_city("pinellas", "Pinellas County", manifest, expand=True)
    for defn in PRICING_PAGES:
        generate_pricing(defn, manifest)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
