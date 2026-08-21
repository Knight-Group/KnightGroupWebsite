#!/usr/bin/env python3
"""Generate the three Home Watch landing pages from a shared service-page shell."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.knightgroup.com"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from service_related import related_card_src  # noqa: E402

ORG = {
    "@type": "Organization",
    "@id": f"{BASE}/#organization",
    "name": "Knight Group Handyman Services LLC",
    "legalName": "Knight Group Handyman Services LLC",
    "url": f"{BASE}/",
    "logo": f"{BASE}/Images/KnightGroupLogo.webp",
    "image": f"{BASE}/Images/KnightGroupLogo.webp",
    "email": "nknight@knightgroup.com",
    "telephone": "+18136493341",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "1225 7th St S",
        "addressLocality": "Safety Harbor",
        "addressRegion": "FL",
        "postalCode": "34695",
        "addressCountry": "US",
    },
    "founder": {"@id": f"{BASE}/#founder"},
    "sameAs": [
        "https://www.facebook.com/KnightGroupServices/",
        "https://www.instagram.com/knight_group_services/",
        "https://x.com/KnightGroupSvcs",
        "https://www.tiktok.com/@knightgroupservices",
        "https://www.pinterest.com/KnightGroupService/",
        "https://www.google.com/maps?cid=10508624668428370015",
    ],
}

FOUNDER = {
    "@type": "Person",
    "@id": f"{BASE}/#founder",
    "name": "Vincent Knight",
    "alternateName": "Vince Knight",
    "jobTitle": "Owner",
    "description": "Owner of Knight Group Handyman Services LLC with journeyman plumbing experience and Florida property management background.",
    "url": f"{BASE}/about#vince-knight",
    "worksFor": {"@id": f"{BASE}/#organization"},
    "knowsAbout": [
        "Handyman services",
        "Home Watch",
        "Snowbird home watch",
        "Vacant property checks",
        "Vacation home monitoring",
        "Property maintenance",
        "Pinellas County home repair",
    ],
}

BUSINESS = {
    "@type": "HomeAndConstructionBusiness",
    "@id": f"{BASE}/#business",
    "name": "Knight Group Handyman Services LLC",
    "url": f"{BASE}/",
    "description": "Knight Group Handyman Services LLC provides registered and insured handyman services and recurring Home Watch / vacant-property checks across Safety Harbor and Pinellas County, Florida.",
    "image": [f"{BASE}/Images/handyman.jpg", f"{BASE}/Images/KGHero.webp"],
    "logo": f"{BASE}/Images/KnightGroupLogo.webp",
    "telephone": "+18136493341",
    "email": "nknight@knightgroup.com",
    "priceRange": "$75-$200",
    "parentOrganization": {"@id": f"{BASE}/#organization"},
    "founder": {"@id": f"{BASE}/#founder"},
    "address": ORG["address"],
    "geo": {"@type": "GeoCoordinates", "latitude": 27.9906, "longitude": -82.6933},
    "areaServed": {"@type": "AdministrativeArea", "name": "Pinellas County, Florida"},
    "knowsAbout": [
        "Handyman services",
        "General home repairs",
        "Home Watch",
        "Home Watch services",
        "Snowbird home watch",
        "Vacant home monitoring",
        "Vacation home watch",
        "Seasonal home checks",
        "Absentee homeowner services",
        "Second-home property checks",
        "Unoccupied house checks",
    ],
    "sameAs": ORG["sameAs"],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": f"{BASE}/#website",
    "url": f"{BASE}/",
    "name": "Knight Group Handyman Services",
    "publisher": {"@id": f"{BASE}/#organization"},
    "inLanguage": "en-US",
}

PINELLAS_FAQS = [
    (
        "What is Home Watch, and is it a home inspection?",
        "Home Watch is a scheduled visual property check with a photo-documented visit report. It is not a licensed home inspection and does not provide a professional opinion of the condition of the home. Reports describe observations from that visit.",
    ),
    (
        "Is Home Watch a private security service?",
        "No. Knight Group documents and reports signs of unexpected or unauthorized entry. We do not patrol, confront anyone, or advertise private security. If a field representative believes someone is inside unexpectedly, they leave and follow the owner’s emergency protocol.",
    ),
    (
        "Are repairs included in Home Watch pricing?",
        "No. Home Watch is observation and reporting. If a visit flags an issue, we notify you with photos. Eligible repairs are quoted separately by Knight Group, and licensed trades are coordinated when the work is outside handyman scope.",
    ),
    (
        "Who is Home Watch for?",
        "Seasonal and snowbird homeowners, second-home owners, vacant investment or for-sale properties, estate and probate houses, landlords between tenants, and owners traveling for an extended period. The service is year-round, not snowbird-only.",
    ),
    (
        "What does a visit report include?",
        "Date, arrival and departure notes, location verification, a property checklist, photographs, issue flags, and a short client-facing summary. That report is the product.",
    ),
    (
        "Which cities do you cover?",
        "Pinellas County, including Safety Harbor, Clearwater, Dunedin, Palm Harbor, Largo, Belleair, Oldsmar, Tarpon Springs, Seminole, and nearby communities we already serve for handyman work. We confirm route fit during intake.",
    ),
    (
        "How do we get started?",
        "Use the qualification form on this page or call (813) 649-3341. Do not send alarm codes, gate codes, or key instructions through the public form. Access details are collected privately after you qualify for service.",
    ),
    (
        "Will Home Watch satisfy my homeowners insurance?",
        "Not automatically. Many Florida policies have a vacancy or unoccupied-home clause after about 30–60 days. Check your policy and share any visit or reporting rules your carrier specifies. We can follow a written property protocol and give you dated photo reports — we cannot promise a claim will be paid.",
    ),
    (
        "Can you check my house while I am away?",
        "Yes. That is the service. Home Watch is a scheduled visit to look through a vacant, seasonal, or second home, take photos, and send you a report. It is not house sitting, live-in caretaking, or a neighbor stopping by when they remember.",
    ),
    (
        "Do you offer snowbird home watch in Pinellas County?",
        "Yes. Snowbirds and seasonal owners who leave for the summer — including Canadian owners with a Pinellas house — are a core audience. Weekly Watch is the usual pick for a long vacancy; Biweekly Watch fits shorter trips. Service is year-round, not only winter.",
    ),
    (
        "Is Home Watch the same as house sitting or a house sitter?",
        "No. A house sitter stays in the home. Home Watch is a short, scheduled property check with a written photo report, then we leave and lock up. We do not live on site, walk pets, or water plants unless that is written into a separate, quoted add-on.",
    ),
    (
        "How often should a vacant Florida home be checked?",
        "Weekly is the default for snowbird season, hurricane season, or a house sitting empty for months. Biweekly works for shorter absences. A one-time property check is for a listing, estate, or a single trip. We confirm frequency during intake.",
    ),
    (
        "Do you do vacation home watch or second-home monitoring?",
        "Yes. Vacation homes, condos used a few weeks a year, and Gulf-coast second homes get the same visual checklist: HVAC and humidity, water, entry points, mail and packages, and a photo report after each stop.",
    ),
    (
        "What happens after a hurricane or tropical storm?",
        "When roads and access are safe, we can add a post-storm property check ($99–$149) on top of the regular plan. That visit is observation and photos, not a repair ticket. Eligible handyman work is quoted separately.",
    ),
]

PRICING_FAQS = [
    (
        "What does weekly Home Watch cost?",
        "Weekly Watch is $329 per month for approximately one visit every seven days. Biweekly Watch is $189 per month. A one-time property check is $125.",
    ),
    (
        "Is onboarding free?",
        "A $99 property-setup fee applies to one-time or short-term checks. It is waived with a recurring plan of three months or longer. A free consultation is for qualified recurring Home Watch prospects, not a drive-out to look around.",
    ),
    (
        "Do Home Watch plans include repair labor?",
        "No. Repair work is separately estimated and billed. That keeps the subscription honest and keeps repair authorization in your hands.",
    ),
    (
        "What extra visits are available?",
        "Exterior-only checks are $59–$75 depending on route. Vendor access starts at $75. Post-storm checks are $99–$149 when roads and access are safe. Arrival and departure property opening or closing is $125–$200.",
    ),
    (
        "Why not just have a neighbor look in?",
        "Neighbors help, and we are not replacing a trusted friend. Home Watch is a dated photo report on a set schedule so you can see HVAC, humidity, water, and entry points from up north or out of state. Repair quotes stay with Knight Group when something is actually wrong.",
    ),
    (
        "Is there a cheaper vacant-property check than weekly interior visits?",
        "Yes. Exterior-only checks start at $59–$75 on route. A one-time interior/exterior property check is $125. Recurring Weekly and Biweekly Watch are for owners who want the same checklist every visit.",
    ),
]

CHECKLIST_FAQS = [
    (
        "Do you run water or flush toilets every visit?",
        "Only when that step is written into the owner’s property protocol. Default visits are visual checks plus photos, temperature, and humidity readings.",
    ),
    (
        "Why check humidity in a vacant Florida home?",
        "Vacant Gulf-coast houses can hold moisture when HVAC is off or set too high. We record interior temperature and humidity so you can see drift between visits, not as a mold inspection.",
    ),
    (
        "Is the checklist a home inspection?",
        "No. It is a consistent visual observation list for a scheduled Home Watch visit. Findings are observations, not a professional opinion of building condition.",
    ),
    (
        "Do you look for water leaks and HVAC failure?",
        "We look for visible water on ceilings, walls, floors, under sinks, and around the water heater, and we note obvious HVAC or thermostat failure. Hidden leaks behind finishes and licensed mechanical diagnosis are outside this checklist.",
    ),
    (
        "Will you bring in mail, packages, and flyers?",
        "We note mail, packages, and flyers that make a vacant house look empty. Bringing items inside can be written into your property protocol; it is not an unbounded concierge errand.",
    ),
]


def faq_schema(page_id: str, faqs: list[tuple[str, str]]) -> dict:
    return {
        "@type": "FAQPage",
        "@id": f"{page_id}#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
        "isPartOf": {"@id": f"{page_id}#webpage"},
    }


def faq_html(section_id: str, heading: str, intro: str, faqs: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"""                        <details class="kg-faq-item">
                            <summary>{q}</summary>
                            <p>{a}</p>
                        </details>"""
        for q, a in faqs
    )
    return f"""            <section class="kg-section kg-service-faq" id="{section_id}-faq" aria-labelledby="{section_id}-faq-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">FAQ</span>
                        <h2 id="{section_id}-faq-heading">{heading}</h2>
                        <p>{intro}</p>
                    </div>
                    <div class="kg-faq-list">
{items}
                    </div>
            </section>"""


def related_grid(cards: list[tuple[str, str, str | None]]) -> str:
    bits = []
    for href, label, img in cards:
        src = img or related_card_src(href)
        if "?v=" not in src:
            src = f"{src}?v=20260821-related-cards"
        bits.append(
            f"""                        <a class="kg-service-related-card" href="{href}">
                            <img src="{src}" alt="{label}" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">{label}</span>
                        </a>"""
        )
    return "\n".join(bits)


QUAL_FORM = """                                <form class="kg-contact-form" action="https://formspree.io/f/xzzvnpne" method="POST" data-kg-guard>
                                    <div class="kg-field">
                                        <label for="hw-name">Your name</label>
                                        <input type="text" id="hw-name" name="name" autocomplete="name" placeholder="First and last name" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-phone">Phone</label>
                                        <input type="tel" id="hw-phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="(813) 555-1234" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-email">Email</label>
                                        <input type="email" id="hw-email" name="email" autocomplete="email" placeholder="you@example.com" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-city">Property city</label>
                                        <input type="text" id="hw-city" name="property_city" placeholder="Clearwater, Dunedin, Palm Harbor…" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-type">Property type</label>
                                        <select id="hw-type" name="property_type" required>
                                            <option value="">Select one</option>
                                            <option>Seasonal / snowbird home</option>
                                            <option>Second home</option>
                                            <option>Vacant investment property</option>
                                            <option>Home awaiting sale</option>
                                            <option>Rental between tenants</option>
                                            <option>Estate / probate</option>
                                            <option>Other</option>
                                        </select>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="hw-sqft">Approximate square footage <span>(optional)</span></label>
                                        <input type="text" id="hw-sqft" name="square_footage" inputmode="numeric" placeholder="e.g. 1,800">
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-away">How often are you away?</label>
                                        <select id="hw-away" name="away_frequency" required>
                                            <option value="">Select one</option>
                                            <option>Most of the year / seasonal</option>
                                            <option>Several months at a time</option>
                                            <option>Weeks at a time</option>
                                            <option>Property is vacant now</option>
                                            <option>One-time check only</option>
                                        </select>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-plan">Plan interest</label>
                                        <select id="hw-plan" name="plan_interest" required>
                                            <option value="">Select one</option>
                                            <option>Weekly Watch ($329/mo)</option>
                                            <option>Biweekly Watch ($189/mo)</option>
                                            <option>One-Time Property Check ($125)</option>
                                            <option>Estate / Premium Watch</option>
                                            <option>Not sure yet</option>
                                        </select>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-interior">Interior access required?</label>
                                        <select id="hw-interior" name="interior_access" required>
                                            <option value="">Select one</option>
                                            <option>Yes — interior checks</option>
                                            <option>No — exterior only</option>
                                            <option>Not sure</option>
                                        </select>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-pool">Pool or spa?</label>
                                        <select id="hw-pool" name="pool" required>
                                            <option value="">Select one</option>
                                            <option>Yes</option>
                                            <option>No</option>
                                        </select>
                                    </div>
                                    <div class="kg-field">
                                        <label for="hw-gate">Gate or HOA access?</label>
                                        <select id="hw-gate" name="gate_hoa" required>
                                            <option value="">Select one</option>
                                            <option>Yes</option>
                                            <option>No</option>
                                        </select>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="hw-start">Desired start date <span>(optional)</span></label>
                                        <input type="text" id="hw-start" name="desired_start" placeholder="Month or approximate date">
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="hw-message">Anything else we should know? <span>(optional)</span></label>
                                        <textarea id="hw-message" name="message" rows="3" placeholder="Property notes — do not include alarm, gate, or lockbox codes"></textarea>
                                    </div>
                                    <p class="kg-form-note">Do not send alarm codes, gate codes, lockbox combinations, or key-hiding instructions on this form. We collect access details privately after you qualify.</p>
                                    <input type="hidden" name="_subject" value="Knight Group Home Watch inquiry">
                                    <input type="hidden" name="request_type" value="Home Watch qualification">
                                    <input type="hidden" name="service_page" value="home-watch-pinellas">
                                    <input type="hidden" name="_next" value="https://www.knightgroup.com/thank-you">
                                    <label class="visually-hidden" for="hw-hp">Leave this field blank</label>
                                    <input class="kg-hp" id="hw-hp" type="text" name="address_2" autocomplete="off" tabindex="-1">
                                    <button type="submit" class="kg-contact-form__submit" data-kg-sending="Sending">Request Home Watch consultation</button>
                                </form>"""


def page(
    *,
    slug: str,
    title: str,
    description: str,
    h1: str,
    eyebrow: str,
    lead: str,
    crumb: str,
    body: str,
    faqs: list[tuple[str, str]],
    faq_heading: str,
    faq_intro: str,
    extra_graph: list[dict],
    related: list[tuple[str, str, str | None]],
    cta_h2: str,
    cta_p: str,
    cta_primary: tuple[str, str],
    cta_secondary: tuple[str, str],
    sidebar_title: str,
    sidebar_p: str,
    form_html: str,
    extra_css: str = "",
) -> str:
    page_id = f"{BASE}/{slug}"
    graph = [
        ORG,
        FOUNDER,
        BUSINESS,
        WEBSITE,
        {
            "@type": "BreadcrumbList",
            "@id": f"{page_id}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
                {"@type": "ListItem", "position": 2, "name": "Services", "item": f"{BASE}/services"},
                {"@type": "ListItem", "position": 3, "name": crumb, "item": page_id},
            ],
        },
        {
            "@type": "WebPage",
            "@id": f"{page_id}#webpage",
            "url": page_id,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{BASE}/#website"},
            "about": {"@id": f"{BASE}/#business"},
            "breadcrumb": {"@id": f"{page_id}#breadcrumb"},
            "inLanguage": "en-US",
            "mainEntity": {"@id": f"{page_id}#service"},
            "primaryImageOfPage": {"@id": f"{page_id}#primary-image"},
        },
        {
            "@type": "ImageObject",
            "@id": f"{page_id}#primary-image",
            "url": f"{BASE}/Images/KGHero.webp",
            "contentUrl": f"{BASE}/Images/KGHero.webp",
            "caption": "Home Watch by Knight Group — scheduled visual property checks in Pinellas County, Florida",
        },
        *extra_graph,
        faq_schema(page_id, faqs),
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=4)
    related_html = related_grid(related)
    css = f"    <style>{extra_css}</style>\n" if extra_css else ""
    return f"""<!DOCTYPE html>
<html lang="en" class="kg-js">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-MNHVDBHG');</script>
<!-- End Google Tag Manager -->
    <script>window.dataLayer = window.dataLayer || [];</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="/JS/canonical-redirect.js"></script>
    <link rel="icon" type="image/png" sizes="32x32" href="/Images/favicon-32x32.png">
    <link rel="apple-touch-icon" href="/Images/apple-touch-icon.png">
    <meta name="theme-color" content="#9a2f2f">
    <meta name="author" content="Knight Group Handyman Services LLC">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{page_id}">
    <script type="application/ld+json">
{ld}
    </script>
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta property="og:url" content="{page_id}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://www.knightgroup.com/Images/knightgroup-og-card-1200x630-clean.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Home Watch by Knight Group in Pinellas County, Florida">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@KnightGroupSvcs">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://www.knightgroup.com/Images/knightgroup-twitter-card-1200x628-phone.png">
    <meta name="twitter:url" content="{page_id}">
<link rel="stylesheet" href="/CSS/header.min.css?v=20260821-home-watch">
    <link rel="stylesheet" href="/CSS/kg-redesign.css?v=20260821-hw-gap">
    <script src="/JS/kg-redesign.js?v=20260821-home-watch" defer></script>
{css}</head>
<body class="kg-page kg-service">
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MNHVDBHG"
height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
    <div id="header-include"></div>
    <main id="main-content">
        <section class="kg-page-hero kg-service-hero" aria-labelledby="{slug}-hero-heading">
            <div class="kg-page-hero__cutout-wrap" aria-hidden="true" data-kg-enter="right">
                <picture>
                    <source srcset="/Images/knight-hero-cutout.webp?v=20260821-home-watch" type="image/webp">
                    <img class="kg-page-hero-cutout" src="/Images/knight-hero-cutout.png" alt="Vince Knight, owner of Knight Group Handyman Services" width="1200" height="800" decoding="async" loading="eager">
                </picture>
            </div>
            <div class="kg-shell kg-page-hero__grid">
                <div class="kg-page-hero__copy">
                    <nav class="kg-breadcrumb" aria-label="Breadcrumb">
                        <a href="/">Home</a><span aria-hidden="true">/</span><a href="/services">Services</a><span aria-hidden="true">/</span><span aria-current="page">{crumb}</span>
                    </nav>
                    <span class="kg-eyebrow">{eyebrow}</span>
                    <h1 id="{slug}-hero-heading">{h1}</h1>
                    <p class="kg-page-hero__lead">{lead}</p>
                </div>
            </div>
        </section>
        <div class="kg-service-stack">
            <div class="kg-shell kg-service-layout">
                <div class="kg-service-main">
            <section class="kg-section kg-service-detail">
                        <div class="kg-service-prose">
{body}
                        </div>
            </section>
{faq_html(slug, faq_heading, faq_intro, faqs)}
            <section class="kg-section kg-service-related" aria-labelledby="related-services-heading">
                    <div class="kg-heading-block">
                        <span class="kg-section-tag">Related pages</span>
                        <h2 id="related-services-heading">Home Watch and property care</h2>
                    </div>
                    <div class="kg-service-related-grid">
{related_html}
                    </div>
            </section>
            <section class="kg-section kg-service-cta">
                    <div class="kg-heading-block">
                        <h2>{cta_h2}</h2>
                        <p>{cta_p}</p>
                    </div>
                    <div class="kg-service-cta__actions">
                        <a href="{cta_primary[0]}" class="kg-btn kg-btn--solid">{cta_primary[1]}</a>
                        <a href="{cta_secondary[0]}" class="kg-btn kg-btn--ghost">{cta_secondary[1]}</a>
                    </div>
            </section>
                </div>
                        <aside class="kg-service-sidebar" aria-labelledby="{slug}-sidebar-heading">
                            <div class="kg-pricing-sidebar-form">
                                <h3 class="kg-sidebar-title" id="{slug}-sidebar-heading">{sidebar_title}</h3>
                                <p>{sidebar_p}</p>
{form_html}
                            </div>
                            <div class="pricing-highlights">
                                <h3>Why Home Watch by Knight Group</h3>
                                <ul>
                                    <li>Photo-documented visit reports</li>
                                    <li>Issue alerts with a path to repair quotes</li>
                                    <li>Same local company for eligible maintenance</li>
                                    <li>Not a home inspection or security patrol</li>
                                    <li>Registered Safety Harbor business</li>
                                    <li>Pinellas County routes</li>
                                </ul>
                            </div>
                            <h3>Quick contact</h3>
                            <div class="pricing-highlights">
                        <a href="tel:+18136493341" class="header-btn-primary kg-header-call" title="Click to call or text (813) 649-3341" aria-label="Call or text (813) 649-3341">
                            <span class="kg-header-call__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" width="18" height="18" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.3 21 3 13.7 3 4c0 .6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
                            </span>
                            <span class="kg-header-call__text">
                                <span class="kg-header-call__label">Call or Text</span>
                                <span class="kg-header-call__number">(813) 649-3341</span>
                            </span>
                        </a>
                                <p style="margin-top:16px;"><strong>Email:</strong> <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a></p>
                                <p><strong>Hours:</strong> Mon&ndash;Fri 8 AM&ndash;5 PM</p>
                            </div>
                        </aside>
            </div>
        </div>
    </main>
    <div id="footer-include"></div>
    <script src="/JS/includes.min.js?v=20260821-home-watch" defer></script>
</body>
</html>
"""


SIMPLE_FORM = """                                <form class="kg-contact-form" action="https://formspree.io/f/xzzvnpne" method="POST" data-kg-guard>
                                    <div class="kg-field">
                                        <label for="{fid}-name">Your name</label>
                                        <input type="text" id="{fid}-name" name="name" autocomplete="name" placeholder="First and last name" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="{fid}-phone">Phone</label>
                                        <input type="tel" id="{fid}-phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="(813) 555-1234" required>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="{fid}-message">Property notes <span>(optional)</span></label>
                                        <textarea id="{fid}-message" name="message" rows="3" placeholder="City, weekly or biweekly, interior vs exterior — no access codes"></textarea>
                                    </div>
                                    <input type="hidden" name="_subject" value="Knight Group Home Watch inquiry">
                                    <input type="hidden" name="request_type" value="Home Watch">
                                    <input type="hidden" name="service_page" value="{slug}">
                                    <input type="hidden" name="_next" value="https://www.knightgroup.com/thank-you">
                                    <label class="visually-hidden" for="{fid}-hp">Leave this field blank</label>
                                    <input class="kg-hp" id="{fid}-hp" type="text" name="address_2" autocomplete="off" tabindex="-1">
                                    <button type="submit" class="kg-contact-form__submit" data-kg-sending="Sending">Request consultation</button>
                                </form>"""


PINELLAS_BODY = """
                            <p><strong>Home Watch by Knight Group</strong> is the Pinellas County answer to “someone to check my house while I’m away.” We run scheduled, photo-documented property checks for snowbird homes, vacation homes, second homes, vacant listings, and absentee-owned houses — then send you the report. If something needs work, the same local company can quote eligible repairs instead of leaving you to find a stranger from another time zone.</p>
                            <p>That is the point of attaching Home Watch to a working property-maintenance company. A visit documents the issue. You get notified. Knight Group can separately quote eligible repairs, or coordinate a licensed trade when the work is outside handyman scope. Repair labor is never bundled into the watch fee.</p>
                            <h2>Snowbird home watch and seasonal house checks</h2>
                            <p>Pinellas has a large seasonal and occasional-use housing stock. Snowbirds who leave for the Midwest, the Northeast, or Canada still need eyes on the house through Florida heat, humidity, and hurricane season. Weekly Watch (~every seven days) is the usual plan for a long vacancy. Biweekly Watch fits shorter trips. The service is year-round — not only winter residents.</p>
                            <p>University of Florida Census-derived housing counts show how common absentee and recreational housing is in this county. That does not mean every vacant unit is a customer — short-term rentals can fall in the same category — but it does show why vacant-home monitoring is a real local search, not a side hobby.</p>
                            <h2>Vacant house checks, vacation homes, and second-home monitoring</h2>
                            <p>People searching <em>home watch services near me</em>, <em>vacant home watch</em>, or <em>vacation home monitoring</em> usually want the same thing: a consistent walkthrough, not a house sitter living on site. We look at entry points, mail and packages, obvious storm or water issues from ground level, HVAC and interior humidity when we have access, and we photograph what we see. Landlords between tenants can pair this with <a href="/rental-turnover-handyman">rental turnover handyman</a> work.</p>
                            <h2>What you get on each visit</h2>
                            <p>Every visit produces a client-facing report: date, arrival and departure, location verification, checklist, photographs, issue flags, and a short summary. See the full <a href="/home-watch-checklist">Florida Home Watch checklist</a> for exterior, interior, and departure items.</p>
                            <h2>Hurricane season and unoccupied-home insurance notes</h2>
                            <p>After a named storm, we can add a post-storm property check when roads and access are safe — related to our <a href="/hurricane-repair-handyman-pinellas">hurricane prep and storm repair</a> page, but billed as a Home Watch visit, not a repair ticket. Many Florida policies limit coverage after a house sits unoccupied for 30–60 days. Dated photo reports can support the paper trail your carrier asks for. They do not automatically satisfy a vacancy clause or guarantee a claim.</p>
                            <h2>What Home Watch is not</h2>
                            <p>It is <strong>not</strong> a licensed home inspection, not house sitting, and not private security. We document and report signs of unexpected or unauthorized entry. We do not patrol, confront anyone, or claim to prevent crime, storm damage, water damage, or mold. Humidity readings are observations, not a mold inspection. If someone appears to be inside unexpectedly, the field representative leaves and follows your written emergency protocol.</p>
                            <h2>Plans, cities, and how to start</h2>
                            <p>Weekly Watch is $329/month. Biweekly Watch is $189/month. A one-time property check is $125. Estate and premium properties start at $429/month. Full breakdown on <a href="/home-watch-pricing">Home Watch pricing</a>. Recurring routes currently run from Safety Harbor through Clearwater, Dunedin, Palm Harbor, Largo, Oldsmar, Tarpon Springs, Seminole, and nearby Pinellas communities we already serve for handyman work. Qualify on this page or call (813) 649-3341 — leave alarm and gate codes off the public form.</p>
"""

PRICING_BODY = """
                            <p>Home Watch pricing is for scheduled visual property checks and reports — the snowbird, vacation-home, and vacant-house monitoring people compare when they search <em>home watch cost</em> or <em>weekly home watch pricing</em>. <strong>Repair labor is always separate.</strong> If a visit finds a leak, a failed HVAC, or other eligible work, Knight Group quotes that job on its own authorization.</p>
                            <table class="kg-hw-table">
                                <caption>Home Watch plans</caption>
                                <thead><tr><th>Plan</th><th>Price</th><th>Scope</th></tr></thead>
                                <tbody>
                                    <tr><td>One-Time Property Check</td><td>$125</td><td>Interior/exterior scheduled visual check and report</td></tr>
                                    <tr><td>Biweekly Watch</td><td>$189/month</td><td>Approximately every two weeks</td></tr>
                                    <tr><td>Weekly Watch</td><td>$329/month</td><td>Approximately every seven days</td></tr>
                                    <tr><td>Estate / Premium Watch</td><td>From $429/month</td><td>Larger property, custom checklist, or greater reporting</td></tr>
                                </tbody>
                            </table>
                            <table class="kg-hw-table">
                                <caption>Add-on and specialty visits</caption>
                                <thead><tr><th>Service</th><th>Price</th><th>Notes</th></tr></thead>
                                <tbody>
                                    <tr><td>Exterior-only check</td><td>$59–$75</td><td>Route-dependent; investor or vacant-property use</td></tr>
                                    <tr><td>Vendor access</td><td>From $75</td><td>Key-in, meet a vendor, basic oversight</td></tr>
                                    <tr><td>Post-storm check</td><td>$99–$149</td><td>When roads and access are safe</td></tr>
                                    <tr><td>Arrival / departure service</td><td>$125–$200</td><td>Property opening or closing checklist</td></tr>
                                </tbody>
                            </table>
                            <h2>Onboarding</h2>
                            <p>Property setup is <strong>$99</strong>, waived with a recurring plan of three months or longer. A free Home Watch consultation is for qualified recurring service — not a complimentary drive-out to look around. Handyman hourly rates on the main <a href="/pricing">pricing</a> page do not apply to Home Watch visits.</p>
                            <p>Compare visit frequency on the <a href="/home-watch-pinellas">Pinellas County Home Watch</a> page, or read <a href="/home-watch-checklist">what we check</a> while you are away.</p>
"""

CHECKLIST_BODY = """
                            <p>This is the working visual checklist Knight Group uses on a scheduled Home Watch visit in Florida — the same list snowbirds, vacation-home owners, and vacant-property investors mean when they ask <em>what does home watch check</em>. It is written so you know what “checking the house while I’m away” actually includes. It is not a licensed home inspection and not a professional opinion of building condition. Findings are <strong>observations</strong> from that visit, with photos.</p>
                            <h2>Exterior</h2>
                            <ul>
                                <li>Visible entry doors and windows</li>
                                <li>Signs of unexpected entry or damage</li>
                                <li>Packages, mail, and flyers</li>
                                <li>Visible storm or wind damage from ground level</li>
                                <li>Obvious irrigation or landscape abnormalities</li>
                                <li>Obvious pool or spa abnormalities if the property has one</li>
                                <li>Exterior HVAC unit observation</li>
                                <li>Visible leaks or standing water</li>
                                <li>Fence and gate condition</li>
                                <li>HOA or city notices left at the property</li>
                            </ul>
                            <h2>Interior</h2>
                            <ul>
                                <li>Interior temperature</li>
                                <li>Humidity reading</li>
                                <li>Thermostat status and obvious HVAC failure</li>
                                <li>Visible water intrusion on ceilings, walls, and floors</li>
                                <li>Under-sink areas and toilets</li>
                                <li>Water heater area</li>
                                <li>Visible pest activity</li>
                                <li>Refrigerator or freezer status if requested</li>
                                <li>Unusual odors</li>
                                <li>Interior doors and windows</li>
                                <li>Electrical power status</li>
                                <li>Run faucets and flush toilets only if included in the owner’s written property protocol</li>
                            </ul>
                            <h2>Departure</h2>
                            <ul>
                                <li>Thermostat restored to the agreed setting</li>
                                <li>Client-requested water setting confirmed</li>
                                <li>Windows and doors secured</li>
                                <li>Alarm activated if applicable and authorized</li>
                                <li>Final photo and visit completed</li>
                            </ul>
                            <h2>The report</h2>
                            <p>Every visit produces date, arrival and departure, location verification, checklist results, photographs, issue flags, and a short summary. If something needs work, that is a separate conversation — see <a href="/home-watch-pinellas">Home Watch in Pinellas County</a> and <a href="/home-watch-pricing">Home Watch pricing</a>.</p>
                            <p>Post-storm visits follow the same observation standard and wait until roads and access are safe. Repair follow-up is quoted separately, including <a href="/hurricane-repair-handyman-pinellas">storm-related handyman work</a> when it fits our scope.</p>
"""

OFFER_CATALOG = {
    "@type": "OfferCatalog",
    "@id": f"{BASE}/home-watch-pricing#offer-catalog",
    "name": "Home Watch plans",
    "itemListElement": [
        {
            "@type": "Offer",
            "name": "Weekly Watch",
            "price": "329.00",
            "priceCurrency": "USD",
            "unitText": "MONTH",
            "description": "Approximately one scheduled Home Watch visit every seven days.",
            "url": f"{BASE}/home-watch-pricing",
        },
        {
            "@type": "Offer",
            "name": "Biweekly Watch",
            "price": "189.00",
            "priceCurrency": "USD",
            "unitText": "MONTH",
            "description": "Approximately one scheduled Home Watch visit every two weeks.",
            "url": f"{BASE}/home-watch-pricing",
        },
        {
            "@type": "Offer",
            "name": "One-Time Property Check",
            "price": "125.00",
            "priceCurrency": "USD",
            "description": "Single scheduled interior/exterior visual check and report.",
            "url": f"{BASE}/home-watch-pricing",
        },
        {
            "@type": "Offer",
            "name": "Estate / Premium Watch",
            "price": "429.00",
            "priceCurrency": "USD",
            "unitText": "MONTH",
            "description": "Starting monthly price for larger properties or custom reporting.",
            "url": f"{BASE}/home-watch-pricing",
        },
    ],
}

SERVICE_NODE = {
    "@type": "Service",
    "@id": f"{BASE}/home-watch-pinellas#service",
    "name": "Home Watch and Vacant Property Checks",
    "alternateName": [
        "Snowbird home watch",
        "Vacant home monitoring",
        "Vacation home watch",
        "Seasonal house checks",
    ],
    "serviceType": "Home Watch, snowbird property checks, and scheduled vacant house monitoring",
    "provider": {"@id": f"{BASE}/#business"},
    "areaServed": {"@type": "AdministrativeArea", "name": "Pinellas County, Florida"},
    "url": f"{BASE}/home-watch-pinellas",
    "description": "Scheduled visual Home Watch services in Pinellas County for snowbirds, vacation homes, second homes, and vacant houses. Photo-documented reports. Not a licensed home inspection, house sitter, or private security service.",
    "hasOfferCatalog": {"@id": f"{BASE}/home-watch-pricing#offer-catalog"},
}

TABLE_CSS = (
    ".kg-hw-table{width:100%;border-collapse:collapse;margin:1.1rem 0 1.5rem;font-size:0.95rem}"
    ".kg-hw-table caption{caption-side:top;text-align:left;font-weight:700;margin:0 0 0.55rem;color:#f0c4c4;"
    "font-family:Playfair Display,Georgia,serif;font-size:1.15rem}"
    ".kg-hw-table th,.kg-hw-table td{border:1px solid rgba(240,196,196,0.22);padding:0.72rem 0.85rem;"
    "text-align:left;vertical-align:top}"
    ".kg-hw-table th{background:rgba(154,47,47,0.42);color:#fff;font-weight:700}"
    ".kg-hw-table td{background:rgba(255,255,255,0.05);color:rgba(255,255,255,0.92)}"
    ".kg-hw-table tbody tr:nth-child(even) td{background:rgba(255,255,255,0.08)}"
    ".kg-form-note{font-size:0.88rem;color:#4b4549;margin:0 0 1rem}"
    ".kg-pricing-sidebar-form select{width:100%;padding:10px 12px;border:1px solid rgba(154,47,47,0.2);"
    "border-radius:10px;font:inherit;color:#1d1c1f;background:#fff}"
)

RELATED = [
    ("/home-watch-pinellas", "Home Watch Pinellas", None),
    ("/home-watch-pricing", "Home Watch pricing", None),
    ("/home-watch-checklist", "Home Watch checklist", None),
    ("/rental-turnover-handyman", "Rental turnover", None),
    ("/hurricane-repair-handyman-pinellas", "Storm property checks", None),
    ("/service-areas", "Service areas", None),
]


def main() -> int:
    pages = {
        "home-watch-pinellas.html": page(
            slug="home-watch-pinellas",
            title="Home Watch Pinellas County | Snowbird and Vacant House Checks",
            description="Home Watch services in Pinellas County for snowbirds, vacation homes, and vacant houses. Weekly and biweekly property checks with photo reports from Safety Harbor.",
            h1="Home Watch Services in Pinellas County: Snowbird, Vacation, and Vacant House Checks",
            eyebrow="Home Watch by Knight Group · Pinellas County",
            lead="Someone local to check your house while you’re away — scheduled snowbird home watch, vacation-home monitoring, and vacant property checks with a photo report after every visit.",
            crumb="Home Watch",
            body=PINELLAS_BODY,
            faqs=PINELLAS_FAQS,
            faq_heading="Home Watch questions",
            faq_intro="Straight answers about scheduled visual property checks — not inspections, not security patrols.",
            extra_graph=[SERVICE_NODE, OFFER_CATALOG],
            related=RELATED[1:],
            cta_h2="Qualify for Home Watch",
            cta_p="Tell us the city, how often you are away, and whether you want weekly or biweekly visits. We will follow up. Do not put access codes on the form.",
            cta_primary=("#hw-name", "Request a consultation"),
            cta_secondary=("/home-watch-pricing", "View Home Watch pricing"),
            sidebar_title="Home Watch qualification",
            sidebar_p="Short intake only. Access codes stay off this form.",
            form_html=QUAL_FORM,
            extra_css=TABLE_CSS,
        ),
        "home-watch-pricing.html": page(
            slug="home-watch-pricing",
            title="Home Watch Pricing | Weekly, Biweekly, and One-Time Pinellas",
            description="Home Watch cost in Pinellas County: weekly $329/month, biweekly $189/month, one-time vacant house check $125, plus storm, vendor-access, and exterior-only options.",
            h1="Home Watch cost in Pinellas County",
            eyebrow="Weekly · Biweekly · One-time vacant house checks",
            lead="Published rates for snowbird home watch, vacation-home monitoring, and vacant property checks. Repairs are quoted separately.",
            crumb="Home Watch pricing",
            body=PRICING_BODY,
            faqs=PRICING_FAQS,
            faq_heading="Pricing questions",
            faq_intro="What weekly, biweekly, and one-time Home Watch visits cost — and what is not included.",
            extra_graph=[
                {**SERVICE_NODE, "@id": f"{BASE}/home-watch-pricing#service", "url": f"{BASE}/home-watch-pricing"},
                OFFER_CATALOG,
            ],
            related=[RELATED[0], RELATED[2], RELATED[3], RELATED[4], RELATED[5], ("/pricing", "Handyman hourly pricing", None)],
            cta_h2="Ready to start a plan?",
            cta_p="Weekly and biweekly Home Watch are recurring property-check plans. Use the Pinellas page to qualify, or call (813) 649-3341.",
            cta_primary=("/home-watch-pinellas", "Go to Home Watch"),
            cta_secondary=("tel:+18136493341", "Call (813) 649-3341"),
            sidebar_title="Ask about a Home Watch plan",
            sidebar_p="City and preferred frequency are enough to start. No access codes.",
            form_html=SIMPLE_FORM.format(fid="hw-price", slug="home-watch-pricing"),
            extra_css=TABLE_CSS,
        ),
        "home-watch-checklist.html": page(
            slug="home-watch-checklist",
            title="Florida Home Watch Checklist | What We Check While You’re Away",
            description="Florida Home Watch checklist for snowbird and vacant homes: HVAC, humidity, water leaks, entry points, mail, and a photo report after each scheduled house check.",
            h1="Florida Home Watch Checklist: What We Check While You're Away",
            eyebrow="Visit scope · Observations, not inspections",
            lead="The practical vacant-house checklist behind Knight Group Home Watch in Pinellas County — humidity, water, HVAC, entry points, and a photo report after every stop.",
            crumb="Home Watch checklist",
            body=CHECKLIST_BODY,
            faqs=CHECKLIST_FAQS,
            faq_heading="Checklist questions",
            faq_intro="What is on a Knight Group Home Watch visit, and what stays off unless you put it in writing.",
            extra_graph=[
                {
                    **SERVICE_NODE,
                    "@id": f"{BASE}/home-watch-checklist#service",
                    "url": f"{BASE}/home-watch-checklist",
                    "name": "Home Watch visit checklist",
                }
            ],
            related=[RELATED[0], RELATED[1], RELATED[3], RELATED[4], RELATED[5], ("/Services/handyman", "Handyman services", None)],
            cta_h2="See plans for Pinellas County",
            cta_p="If this checklist matches what you want while you are away, review weekly and biweekly Home Watch on the Pinellas page.",
            cta_primary=("/home-watch-pinellas", "Home Watch in Pinellas County"),
            cta_secondary=("/home-watch-pricing", "Home Watch pricing"),
            sidebar_title="Ask about this checklist",
            sidebar_p="Tell us the city and whether you need interior access. No alarm or gate codes.",
            form_html=SIMPLE_FORM.format(fid="hw-check", slug="home-watch-checklist"),
            extra_css=TABLE_CSS,
        ),
    }
    for name, html in pages.items():
        path = ROOT / name
        path.write_text(html, encoding="utf-8")
        print(f"Wrote {path.name} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
