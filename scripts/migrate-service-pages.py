#!/usr/bin/env python3
"""Rebuild legacy Services/*.html pages with the kg-page dark redesign template."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_pool import (  # noqa: E402
    SERVICE_PARENT_TO_CATEGORY,
    prose_with_inline_gallery,
)
from page_meta import clip_title, resolve_description  # noqa: E402
from schema_graph import build_graph_for_page  # noqa: E402
from service_expansions import EXPANSIONS, EXTRA_FAQ  # noqa: E402
from service_sidebar import render_service_sidebar  # noqa: E402

ROOT = SCRIPT_DIR.parent
SERVICES = ROOT / "Services"
VERSION = "20260622-compact-buttons"

SKIP = {
    "handcraftedfurniture&resins.html",
    "programming&databases.html",
    "index.html",
}

HERO_CUTOUT_TEMPLATE = """
            <div class="kg-page-hero__cutout-wrap" aria-hidden="true" data-kg-enter="right">
                <picture>
                    <source srcset="../Images/knight-hero-cutout.webp?v={version}" type="image/webp">
                    <img class="kg-page-hero-cutout" src="../Images/knight-hero-cutout.png" alt="" width="1200" height="800" decoding="async" loading="eager">
                </picture>
            </div>"""

SCOPE_DISCLAIMER_HTML = """
                            <div class="kg-scope-disclaimer">
                                <p><strong>Handyman scope notice:</strong> Knight Group provides handyman-scope fixture replacement, minor repairs, and troubleshooting using existing connections. We do not perform work requiring a licensed plumbing, electrical, HVAC, or general contractor license. If a job requires a permit or licensed trade contractor, we identify that before work begins and refer or coordinate appropriately.</p>
                            </div>"""

SCOPE_SLUGS = {"plumbing-services", "electrical-work", "emergency-services"}

from service_related import SERVICE_CARD_IMAGES, resolve_card_image  # noqa: E402

SERVICE_LABELS = {
    "general-repairs": "General Repairs",
    "plumbing-services": "Plumbing Services",
    "electrical-work": "Electrical Work",
    "carpentry-framing": "Carpentry & Framing",
    "painting-finishing": "Painting & Finishing",
    "home-renovations": "Home Renovations",
    "doors-windows": "Doors & Windows",
    "custom-projects": "Custom Projects",
    "emergency-services": "Emergency Services",
    "handyman": "Handyman Services",
}


def clean_text(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\ufffd", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def esc(value: str) -> str:
    return html.escape(clean_text(value))


def extract(pattern: str, text: str, flags: int = re.S) -> str:
    match = re.search(pattern, text, flags)
    return clean_text(match.group(1)) if match else ""


def extract_all(pattern: str, text: str, flags: int = re.S) -> list[str]:
    return [clean_text(m) for m in re.findall(pattern, text, flags)]


def fix_content_links(content: str, slug: str) -> str:
    content = re.sub(r'href="\.\./([^"]+)"', r'href="/\1"', content)
    content = re.sub(
        r'href="(?!https?://|/|#|mailto:|tel:)([^"]+)"',
        lambda m: f'href="/Services/{m.group(1).strip("/").replace(".html", "")}"',
        content,
    )
    content = content.replace('class="service-list"', "")
    content = re.sub(r"<ul\s+>", "<ul>", content)
    return content


def merge_faq_items(
    legacy_items: list[tuple[str, str]],
    extra_items: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    merged: list[tuple[str, str]] = []
    seen: set[str] = set()
    for question, answer in legacy_items + extra_items:
        key = question.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append((question, answer))
    return merged


def extract_prose_block(page_html: str) -> str:
    start = page_html.find('<div class="service-details">')
    sidebar = page_html.find('<div class="service-sidebar">', start)
    if start == -1 or sidebar == -1:
        return ""
    start += len('<div class="service-details">')
    block = page_html[start:sidebar].strip()
    block = re.sub(r"</div>\s*$", "", block, flags=re.I)
    return block.strip()


def extract_gallery_block(page_html: str) -> str:
    match = re.search(
        r'<section class="gallery-section">(.*?)</section>',
        page_html,
        re.S | re.I,
    )
    if not match:
        return ""
    block = match.group(1)
    block = re.sub(r"<form\b.*?</form>", "", block, flags=re.S | re.I)
    block = fix_content_links(block, "")
    return f'<section class="kg-service-gallery">{block}</section>'


def transform_prose(raw_html: str) -> str:
    raw_html = re.sub(r"<form\b.*?</form>", "", raw_html, flags=re.S | re.I)
    raw_html = re.sub(r'<div class="map-wrapper">.*?</div>', "", raw_html, flags=re.S | re.I)
    raw_html = re.sub(r'<div class="experience-card">', '<div class="kg-service-callout">', raw_html)
    raw_html = re.sub(r'<div class="process-steps">', '<div class="kg-service-steps">', raw_html)
    raw_html = re.sub(r'<div class="process-step">', '<div class="kg-service-step">', raw_html)
    raw_html = re.sub(r'<div class="warning-box">', '<div class="kg-service-callout">', raw_html)
    raw_html = re.sub(r"(<h[1-6][^>]*>)\s*\?\?\s*", r"\1", raw_html)
    raw_html = re.sub(r"\?\?\s*Safety First", "Safety First", raw_html)
    raw_html = re.sub(r"1ï¿½2", "1\u20132", raw_html)
    raw_html = re.sub(r"ï¿½", "\u2014", raw_html)
    raw_html = re.sub(r"\ufffd+", "", raw_html)
    raw_html = fix_content_links(raw_html, "")
    raw_html = re.sub(r'\s*style="[^"]*"', "", raw_html)
    raw_html = re.sub(r"\s+</ul>", "</ul>", raw_html)
    return raw_html.strip()


def extract_faq_items(page_html: str) -> list[tuple[str, str]]:
    block = extract(r'<section class="faq-section".*?>(.*?)</section>', page_html)
    if not block:
        return []
    items = []
    for summary, answer in re.findall(
        r"<details class=\"faq-item\">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>",
        block,
        re.S,
    ):
        items.append((html.unescape(clean_text(summary)), html.unescape(clean_text(answer))))
    return items


def extract_related(page_html: str) -> list[tuple[str, str]]:
    block = extract(r'<section class="related-services".*?>(.*?)</section>', page_html)
    if not block:
        return []
    links = []
    for href, label in re.findall(r'<a href="([^"]+)" class="related-card">(.*?)</a>', block, re.S):
        slug = href.strip("/").split("/")[-1].replace(".html", "")
        links.append((f"/Services/{slug}", clean_text(label)))
    return links


def faq_entities(items: list[tuple[str, str]]) -> list[dict]:
    return [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in items
    ]


def extract_json_ld(page_html: str) -> str:
    scripts = re.findall(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        page_html,
        re.S,
    )
    if not scripts:
        return ""
    # Prefer the largest @graph payload (richest schema bundle).
    payload = max(scripts, key=len)
    return payload.strip()


def render_faq(items: list[tuple[str, str]], slug: str) -> str:
    if not items:
        return ""
    rows = []
    for question, answer in items:
        rows.append(
            f"""                        <details class="kg-faq-item">
                            <summary>{html.escape(question)}</summary>
                            <p>{html.escape(answer)}</p>
                        </details>"""
        )
    return f"""
            <section class="kg-section kg-service-faq" id="{slug}-faq" aria-labelledby="{slug}-faq-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">FAQ</span>
                        <h2 id="{slug}-faq-heading">Frequently asked questions</h2>
                        <p>Common questions homeowners ask before booking this type of work in Pinellas County.</p>
                    </div>
                    <div class="kg-faq-list">
{chr(10).join(rows)}
                    </div>
            </section>"""


def render_related(links: list[tuple[str, str]]) -> str:
    if not links:
        return ""
    cards = []
    for href, label in links:
        if not href.startswith("/Services/"):
            continue
        image = resolve_card_image(href)
        if image.startswith("cities/"):
            img_src = f"../Images/{image}"
        else:
            img_src = f"../Images/services/{image}"
        cards.append(
            f"""                        <a class="kg-service-related-card" href="{href}">
                            <img src="{img_src}?v={VERSION}" alt="" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">{html.escape(label)}</span>
                        </a>"""
        )
    if not cards:
        return ""
    return f"""
            <section class="kg-section kg-service-related" aria-labelledby="related-services-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">Related services</span>
                        <h2 id="related-services-heading">Other services we offer</h2>
                    </div>
                    <div class="kg-service-related-grid">
{chr(10).join(cards)}
                    </div>
            </section>"""


def render_page(slug: str, page_html: str) -> str:
    label = SERVICE_LABELS.get(slug, slug.replace("-", " ").title())
    rel_path = f"Services/{slug}.html"
    raw_title = extract(r"<title>(.*?)</title>", page_html) or f"{label} | Knight Group"
    title = clip_title(html.unescape(raw_title))
    raw_description = extract(r'<meta name="description" content="(.*?)"', page_html)
    keywords = extract(r'<meta name="keywords" content="(.*?)"', page_html)
    hero_h1 = extract(r'<section class="service-hero">.*?<h1>(.*?)</h1>', page_html) or label
    hero_lead = extract(r'<section class="service-hero">.*?<p>(.*?)</p>', page_html)
    legacy_prose = transform_prose(extract_prose_block(page_html))
    expansion = EXPANSIONS.get(slug, "").strip()
    prose = legacy_prose
    if expansion:
        prose = f"{legacy_prose}\n\n{expansion}" if legacy_prose else expansion
    if slug in SCOPE_SLUGS:
        prose = f"{SCOPE_DISCLAIMER_HTML}\n{prose}"
    prose = prose_with_inline_gallery(
        prose,
        slug,
        "../",
        category=SERVICE_PARENT_TO_CATEGORY.get(slug),
        alt_fallback=f"{label} project photo in Pinellas County",
    )
    faq_items = merge_faq_items(extract_faq_items(page_html), EXTRA_FAQ.get(slug, []))
    related = extract_related(page_html)

    if not hero_lead:
        hero_lead = raw_description or ""

    description = resolve_description(rel_path, html.unescape(hero_lead or raw_description or ""))
    canonical = f"https://www.knightgroup.com/Services/{slug}"
    meta = {"title": title, "description": description, "canonical": canonical}
    service = {
        "name": clean_text(hero_h1),
        "serviceType": clean_text(hero_h1),
        "description": description,
        "image": f"{slug}.jpg",
    }
    json_ld = json.dumps(
        build_graph_for_page(
            page_key="service-detail",
            meta=meta,
            faq_entities=faq_entities(faq_items),
            service=service,
        ),
        indent=4,
        ensure_ascii=False,
    )
    cutout_wrap = HERO_CUTOUT_TEMPLATE.format(version=VERSION)
    sidebar_html = render_service_sidebar(slug, label)

    return f"""<!DOCTYPE html>
<html lang="en" class="kg-js">
<head>
    <script>window.dataLayer = window.dataLayer || [];</script>
    <script>
    var _gtmLoaded = false;
    function _loadGTM() {{
        if (_gtmLoaded) return;
        _gtmLoaded = true;
        var s = document.createElement('script');
        s.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG';
        s.async = true;
        document.head.appendChild(s);
        window.dataLayer.push({{'gtm.start': new Date().getTime(), event: 'gtm.js'}});
    }}
    if ('requestIdleCallback' in window) {{
        requestIdleCallback(_loadGTM, {{ timeout: 5000 }});
    }} else {{
        setTimeout(_loadGTM, 5000);
    }}
    </script>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="../JS/canonical-redirect.js"></script>
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <link rel="icon" type="image/png" sizes="32x32" href="../Images/favicon-32x32.png">
    <link rel="apple-touch-icon" href="/Images/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="#9a2f2f">
    <meta name="msapplication-TileColor" content="#14161d">
    <meta name="author" content="Knight Group Handyman Services LLC">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">

    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:image" content="https://www.knightgroup.com/Images/handyman.jpg">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Knight Group Handyman Services">
    <meta property="og:locale" content="en_US">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@KnightGroupSvcs">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="https://www.knightgroup.com/Images/handyman.jpg">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="geo.region" content="US-FL">
    <meta name="geo.placename" content="Safety Harbor, Pinellas County, Florida">
    <meta name="keywords" content="{esc(keywords)}">

    <script type="application/ld+json">
{json_ld}
    </script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="font" href="https://fonts.gstatic.com/s/playfairdisplay/v40/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiunDXbtM.woff2" crossorigin>
    <style>@font-face{{font-family:'Playfair Display';font-style:normal;font-weight:700;font-display:optional;src:url('https://fonts.gstatic.com/s/playfairdisplay/v40/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiunDXbtM.woff2') format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}</style>

    <link rel="stylesheet" href="../CSS/header.min.css?v={VERSION}">
    <link rel="stylesheet" href="../CSS/kg-redesign.css?v={VERSION}">
    <script src="../JS/kg-redesign.js?v={VERSION}" defer></script>
    <script>window.addEventListener('load',function(){{setTimeout(function(){{var l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=optional';document.head.appendChild(l)}},1500)}})</script>
</head>
<body class="kg-page kg-service">
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MNHVDBHG" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>

    <div id="header-include"></div>

    <main id="main-content">
        <section class="kg-page-hero kg-service-hero" aria-labelledby="{slug}-hero-heading">
{cutout_wrap}
            <div class="kg-shell kg-page-hero__grid">
                <div class="kg-page-hero__copy">
                    <nav class="kg-breadcrumb" aria-label="Breadcrumb">
                        <a href="/">Home</a>
                        <span aria-hidden="true">/</span>
                        <a href="/services">Services</a>
                        <span aria-hidden="true">/</span>
                        <span aria-current="page">{esc(label)}</span>
                    </nav>
                    <span class="kg-eyebrow">Safety Harbor · Pinellas County</span>
                    <h1 id="{slug}-hero-heading" data-kg-enter="left">{esc(hero_h1)}</h1>
                    <p class="kg-page-hero__lead" data-kg-enter="left" style="--kg-enter-delay: 80ms;">{esc(hero_lead)}</p>
                </div>
            </div>
        </section>

        <div class="kg-service-stack">
            <div class="kg-shell kg-service-layout">
                <div class="kg-service-main">
            <section class="kg-section kg-service-detail" aria-labelledby="{slug}-detail-heading">
                        <div class="kg-service-prose">
                            {prose}
                        </div>
            </section>
{render_faq(faq_items, slug)}
{render_related(related)}
            <section class="kg-section kg-service-cta" aria-labelledby="{slug}-cta-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">Next step</span>
                        <h2 id="{slug}-cta-heading">Ready to schedule {esc(label.lower())}?</h2>
                        <p>Tell us what needs attention, where the property is located, and when you would like help. We will confirm scope and pricing before work starts.</p>
                    </div>
                    <div class="kg-service-cta__actions">
                        <a href="/booking" class="kg-btn kg-btn--solid">Book a free estimate</a>
                        <a href="/services" class="kg-btn kg-btn--ghost">Browse all services</a>
                        <a href="/galleries" class="kg-btn kg-btn--ghost">See project gallery</a>
                    </div>
            </section>
                </div>

{sidebar_html}
            </div>
        </div>
    </main>

    <div id="footer-include"></div>

    <script src="../JS/includes.min.js?v={VERSION}" defer></script>
</body>
</html>
"""


def main() -> int:
    updated = 0
    for path in sorted(SERVICES.glob("*.html")):
        if path.name in SKIP:
            continue
        slug = path.stem
        legacy = SCRIPT_DIR / f"legacy-{slug}.html"
        if not legacy.is_file():
            print(f"skip (no legacy source): {path.name}")
            continue
        source = legacy.read_text(encoding="utf-8", errors="replace")
        rendered = render_page(slug, source)
        if not extract_prose_block(source).strip() and slug not in EXPANSIONS:
            print(f"warning: thin content for {path.name}")
        path.write_text(rendered, encoding="utf-8", newline="\n")
        updated += 1
        print(f"migrated: {path.name}")
    print(f"Done. Updated {updated} service pages.")
    from audit_gallery_refs import main as audit_gallery_refs

    if audit_gallery_refs() != 0:
        print("Gallery audit failed.", file=sys.stderr)
        return 1
    print("Gallery audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
