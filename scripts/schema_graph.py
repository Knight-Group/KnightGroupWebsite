#!/usr/bin/env python3
"""Build unified JSON-LD @graph blocks for Knight Group canonical pages."""

from __future__ import annotations

import copy
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from business_facts import (  # noqa: E402
    BUSINESS_DESCRIPTION,
    eligible_regions,
    geography_for_url,
    load_facts,
    overall_area_served,
    vince_id,
)

ROOT = Path(__file__).resolve().parents[1]
SEO = ROOT / "seo"
BASE = "https://www.knightgroup.com"
BUSINESS_ID = f"{BASE}/#business"
ORG_ID = f"{BASE}/#organization"
VINCE_ID = vince_id()
FOUNDER_ID = VINCE_ID
WEBSITE_ID = f"{BASE}/#website"
PRICING_CATALOG_ID = f"{BASE}/pricing#offer-catalog"
DEFAULT_SERVICE_IMAGE = f"{BASE}/Images/handyman.jpg"

AREA_SERVED = overall_area_served()

SERVICE_IMAGES = {
    item["slug"]: item["image"]
    for item in json.loads((SEO / "service-catalog.json").read_text(encoding="utf-8"))["services"]
}


def _load(name: str) -> dict[str, Any]:
    return json.loads((SEO / name).read_text(encoding="utf-8"))


def extract_meta(html: str) -> dict[str, str]:
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html, re.I)
    canonical = re.search(r'<link rel="canonical" href="([^"]*)"', html, re.I)
    return {
        "title": title.group(1).strip() if title else "",
        "description": desc.group(1).strip() if desc else "",
        "canonical": canonical.group(1).strip() if canonical else "",
    }


def _clean_text(value: str) -> str:
    text = re.sub(r"<a[^>]*>(.*?)</a>", r"\1", value, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\ufffd", "-")
    return re.sub(r"\s+", " ", text).strip()


def extract_faq_entities(html: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for block in re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.S | re.I,
    ):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        graphs = data.get("@graph", [data])
        if not isinstance(graphs, list):
            graphs = [graphs]
        for node in graphs:
            if node.get("@type") == "FAQPage" and node.get("mainEntity"):
                entities = node["mainEntity"]
    return entities


def extract_faq_from_html(html_content: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for summary, answer in re.findall(
        r"<summary>(.*?)</summary>\s*<p>(.*?)</p>",
        html_content,
        flags=re.S | re.I,
    ):
        question = _clean_text(summary)
        text = _clean_text(answer)
        if not question or not text:
            continue
        entities.append(
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": text},
            }
        )
    return entities


def extract_page_faq(html_content: str) -> list[dict[str, Any]]:
    html_faq = extract_faq_from_html(html_content)
    if html_faq:
        return html_faq
    return extract_faq_entities(html_content)


def extract_howto(html_content: str) -> dict[str, Any] | None:
    match = re.search(
        r'<ol class="kg-howto-steps"[^>]*data-howto-name="([^"]+)"[^>]*>(.*?)</ol>',
        html_content,
        flags=re.S | re.I,
    )
    if not match:
        return None
    name = html.unescape(match.group(1)).strip()
    items = re.findall(
        r"<li>\s*<strong>(.*?)</strong>\s*<p>(.*?)</p>\s*</li>",
        match.group(2),
        flags=re.S | re.I,
    )
    if len(items) < 2:
        return None
    return {
        "name": name,
        "steps": [
            {
                "@type": "HowToStep",
                "position": index,
                "name": _clean_text(title),
                "text": _clean_text(text),
            }
            for index, (title, text) in enumerate(items, start=1)
        ],
    }


def extract_gallery_project_image(html_content: str) -> tuple[str, str] | None:
    match = re.search(
        r'<div class="kg-gallery-project-images">.*?<img src="([^"]+)"[^>]*alt="([^"]*)"',
        html_content,
        flags=re.S | re.I,
    )
    if not match:
        return None
    src = match.group(1).strip()
    alt = _clean_text(match.group(2))
    if src.startswith("/"):
        src = f"{BASE}{src}"
    elif not src.startswith("http"):
        src = f"{BASE}/{src.lstrip('/')}"
    return src, alt


def image_rights_metadata() -> dict[str, Any]:
    return {
        "creditText": "Knight Group Handyman Services LLC",
        "copyrightNotice": "Copyright 2026 Knight Group Handyman Services LLC. All rights reserved.",
        "license": f"{BASE}/PolicyPages/terms",
        "acquireLicensePage": f"{BASE}/contact",
        "creator": {"@id": ORG_ID},
    }


def build_image_object(
    *,
    image_id: str,
    image_url: str,
    name: str,
    description: str,
) -> dict[str, Any]:
    node = {
        "@type": "ImageObject",
        "@id": image_id,
        "url": image_url,
        "contentUrl": image_url,
        "name": name,
        "description": description,
    }
    node.update(image_rights_metadata())
    return node


def _apply_live_reviews(entity: dict[str, Any]) -> dict[str, Any]:
    feed_path = ROOT / "data" / "google-reviews.json"
    if not feed_path.exists():
        return entity
    try:
        feed = json.loads(feed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return entity
    count = feed.get("reviewCount")
    rating = feed.get("ratingValue")
    if not count:
        return entity
    agg = entity.setdefault("aggregateRating", {"@type": "AggregateRating"})
    agg["reviewCount"] = str(int(count))
    if rating is not None:
        agg["ratingValue"] = f"{float(rating):.1f}"
    agg.setdefault("bestRating", "5")
    agg.setdefault("worstRating", "1")
    return entity


def business_entity(*, include_reviews: bool = False) -> dict[str, Any]:
    entity = copy.deepcopy(_load("knight-group-business-entity.json"))
    facts = load_facts()
    entity.pop("priceRange", None)
    entity["paymentAccepted"] = list(facts["payments"]["accepted"])
    entity["founder"] = {"@id": VINCE_ID}
    entity["description"] = BUSINESS_DESCRIPTION
    entity["areaServed"] = overall_area_served()
    entity["knowsAbout"] = list(facts["knowsAbout"])
    _apply_live_reviews(entity)
    if include_reviews:
        entity["review"] = _load("knight-group-reviews-home.json")
    return entity


def website_entity() -> dict[str, Any]:
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": f"{BASE}/",
        "name": "Knight Group Handyman Services",
        "description": "Registered and insured handyman services in Safety Harbor, Pinellas County, Hillsborough County, and Pasco County, Florida.",
        "publisher": {"@id": BUSINESS_ID},
        "inLanguage": "en-US",
    }


def breadcrumb_entity(url: str, crumbs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": crumb["name"],
                "item": crumb["item"],
            }
            for index, crumb in enumerate(crumbs)
        ],
    }


def webpage_entity(
    *,
    url: str,
    meta: dict[str, str],
    page_type: str = "WebPage",
    main_entity_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "@type": page_type,
        "@id": f"{url}#webpage",
        "url": url,
        "name": meta["title"],
        "description": meta["description"],
        "isPartOf": {"@id": WEBSITE_ID},
        "about": {"@id": BUSINESS_ID},
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
        "inLanguage": "en-US",
    }
    if main_entity_id:
        node["mainEntity"] = {"@id": main_entity_id}
    if extra:
        node.update(extra)
    return node


def _combo_city_slug(url_slug: str) -> str:
    try:
        from seo_page_data import COUNTY_REGIONS

        city_slugs = sorted(
            (city["slug"] for region in COUNTY_REGIONS for city in region["cities"]),
            key=len,
            reverse=True,
        )
        for city_slug in city_slugs:
            if url_slug.startswith(f"{city_slug}-"):
                return city_slug
    except ImportError:
        pass
    return url_slug.split("-")[0]


def _url_slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def _geo_breadcrumb_label(url: str, meta: dict[str, str], service: dict[str, str] | None) -> str:
    if service and service.get("name"):
        return str(service["name"])
    title = meta.get("title", "")
    if "|" in title:
        return title.split("|")[0].strip()
    return _url_slug(url).replace("-", " ").title()


def _append_geo_service_graph(
    graph: list[dict[str, Any]],
    *,
    url: str,
    meta: dict[str, str],
    service: dict[str, str] | None,
    crumbs: list[dict[str, str]],
    hero_image_file: str = "handyman.webp",
) -> str:
    label = _geo_breadcrumb_label(url, meta, service)
    crumbs.extend(
        [
            {"name": "Service Areas", "item": f"{BASE}/service-areas"},
            {"name": label, "item": url},
        ]
    )
    service_payload = service or {
        "name": label,
        "serviceType": "Handyman services",
        "description": meta["description"],
        "image": hero_image_file.replace(".webp", ".jpg"),
    }
    graph.append(service_entity(url=url, service=service_payload))
    service_id = f"{url}#service"
    image_node = build_image_object(
        image_id=f"{url}#primary-image",
        image_url=f"{BASE}/Images/{service_payload['image']}",
        name=f"{service_payload['name']} project photo",
        description=service_payload["description"],
    )
    graph.append(image_node)
    return service_id


def service_entity(
    *,
    url: str,
    service: dict[str, str],
    include_offer_catalog_ref: bool = True,
    area_served: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    image = f"{BASE}/Images/{service['image']}"
    served = area_served if area_served is not None else geography_for_url(url)
    node: dict[str, Any] = {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": service["name"],
        "description": service["description"],
        "serviceType": service["serviceType"],
        "provider": {"@id": BUSINESS_ID},
        "url": url,
        "image": image,
        "areaServed": served,
        "offers": {
            "@type": "Offer",
            "url": f"{BASE}/booking",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "eligibleRegion": eligible_regions(served),
        },
    }
    if include_offer_catalog_ref:
        node["hasOfferCatalog"] = {"@id": PRICING_CATALOG_ID}
    return node


def _nested_service(name: str, service_type: str) -> dict[str, Any]:
    return {
        "@type": "Service",
        "name": name,
        "serviceType": service_type,
        "provider": {"@id": BUSINESS_ID},
        "image": DEFAULT_SERVICE_IMAGE,
    }


def pricing_offer_catalog() -> dict[str, Any]:
    return {
        "@type": "OfferCatalog",
        "@id": PRICING_CATALOG_ID,
        "name": "Knight Group Handyman Pricing",
        "url": f"{BASE}/pricing",
        "provider": {"@id": BUSINESS_ID},
        "itemListElement": [
            {
                "@type": "Offer",
                "name": "Standard handyman visit",
                "description": "Common handyman repairs, punch-list work, drywall patches, door adjustments, caulking, screens, and shelving.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": _nested_service("Standard handyman visit", "Handyman services"),
                "priceSpecification": [
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "150",
                        "priceCurrency": "USD",
                        "name": "First hour",
                        "unitText": "hour",
                    },
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "75",
                        "priceCurrency": "USD",
                        "name": "Additional hour",
                        "unitText": "hour",
                    },
                ],
            },
            {
                "@type": "Offer",
                "name": "Minor plumbing repair visit",
                "description": "Faucet, shutoff, fixture, and small-leak repairs on existing connections. Repipes, sewer mains, and gas work are referred.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": _nested_service(
                    "Minor plumbing repair visit",
                    "Handyman plumbing fixture repair and minor plumbing repair",
                ),
                "priceSpecification": [
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "150",
                        "priceCurrency": "USD",
                        "name": "First hour",
                        "unitText": "hour",
                    },
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "75",
                        "priceCurrency": "USD",
                        "name": "Additional hour",
                        "unitText": "hour",
                    },
                ],
            },
            {
                "@type": "Offer",
                "name": "Specialty install and repair visit",
                "description": "Heavier installs, higher-liability work, fixture installs, TV mounting, and appliance hookup support.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": _nested_service(
                    "Specialty install and repair visit",
                    "Specialty handyman work",
                ),
                "priceSpecification": [
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "200",
                        "priceCurrency": "USD",
                        "name": "First hour",
                        "unitText": "hour",
                    },
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "100",
                        "priceCurrency": "USD",
                        "name": "Additional hour",
                        "unitText": "hour",
                    },
                ],
            },
            {
                "@type": "Offer",
                "name": "Urgent property-damage response",
                "description": "Urgent property-damage response during posted hours and after-hours callback when available. Not a 24/7 dispatch service. No guaranteed response time.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": _nested_service(
                    "Urgent property-damage response",
                    "Urgent property-damage response",
                ),
                "priceSpecification": [
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "150",
                        "priceCurrency": "USD",
                        "name": "Regular-hours emergency fee",
                    },
                    {
                        "@type": "UnitPriceSpecification",
                        "price": "200",
                        "priceCurrency": "USD",
                        "name": "After-hours emergency fee",
                    },
                ],
            },
        ],
    }


def gallery_entities(manifest: dict[str, Any], meta: dict[str, str]) -> list[dict[str, Any]]:
    url = f"{BASE}/galleries"
    image_nodes: list[dict[str, Any]] = []
    project_nodes: list[dict[str, Any]] = []
    image_refs: list[dict[str, str]] = []
    part_refs: list[dict[str, str]] = []

    for group in manifest.get("groups", [])[:12]:
        if not group.get("images"):
            continue
        image = group["images"][0]
        src = image["src"].replace("\\", "/")
        image_url = f"{BASE}/{src}"
        image_id = f"{url}#image-{group['id']}"
        project_id = f"{url}#project-{group['id']}"
        image_node = build_image_object(
            image_id=image_id,
            image_url=image_url,
            name=image.get("title") or group["title"],
            description=image.get("description") or group["description"],
        )
        project_node = {
            "@type": "CreativeWork",
            "@id": project_id,
            "name": group["title"],
            "description": group["description"],
            "about": {
                "@type": "Service",
                "name": group.get("category", "Handyman project"),
                "provider": {"@id": BUSINESS_ID},
                "image": image_url,
            },
            "locationCreated": {
                "@type": "AdministrativeArea",
                "name": "Pinellas County, Florida",
            },
            "provider": {"@id": BUSINESS_ID},
            "image": {"@id": image_id},
        }
        image_nodes.append(image_node)
        project_nodes.append(project_node)
        image_refs.append({"@id": image_id})
        part_refs.append({"@id": project_id})

    gallery = {
        "@type": "ImageGallery",
        "@id": f"{url}#gallery",
        "name": meta["title"],
        "description": meta["description"],
        "url": url,
        "provider": {"@id": BUSINESS_ID},
        "about": {"@id": BUSINESS_ID},
        "locationCreated": {
            "@type": "AdministrativeArea",
            "name": "Pinellas County, Florida",
        },
        "image": image_refs,
        "hasPart": part_refs,
    }
    project_list = {
        "@type": "ItemList",
        "@id": f"{url}#project-list",
        "name": "Knight Group handyman project gallery",
        "description": "Completed handyman project photos across Pinellas County, Florida.",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": group["title"],
                "url": f"{url}#project-{group['id']}",
                "item": {"@id": f"{url}#project-{group['id']}"},
            }
            for index, group in enumerate(manifest.get("groups", [])[:12])
            if group.get("images")
        ],
    }
    return [gallery, project_list, *image_nodes, *project_nodes]


def base_graph(*, include_reviews: bool = False) -> list[dict[str, Any]]:
    return [
        _load("knight-group-organization.json"),
        _load("knight-group-founder.json"),
        business_entity(include_reviews=include_reviews),
        website_entity(),
    ]


def build_graph_for_page(
    *,
    page_key: str,
    meta: dict[str, str],
    faq_entities: list[dict[str, Any]],
    service: dict[str, str] | None = None,
    html_content: str = "",
) -> dict[str, Any]:
    url = meta["canonical"].rstrip("/")
    if page_key == "home":
        url = f"{BASE}/"
    graph = base_graph(include_reviews=page_key == "home")
    crumbs = [{"name": "Home", "item": f"{BASE}/"}]
    main_entity_id: str | None = BUSINESS_ID
    page_type = "WebPage"
    extra: dict[str, Any] = {}

    if page_key == "home":
        hero_image = build_image_object(
            image_id=f"{url}#primary-image",
            image_url=f"{BASE}/Images/KGHero.webp",
            name="Knight Group Handyman Services project photo",
            description="Knight Group Handyman Services serving Safety Harbor and Pinellas County, Florida.",
        )
        graph.append(hero_image)
        extra["primaryImageOfPage"] = {"@id": hero_image["@id"]}
    elif page_key == "services-hub":
        crumbs.append({"name": "Services", "item": f"{BASE}/services"})
        main_entity_id = f"{BASE}/services#itemlist"
        graph.append(
            {
                "@type": "ItemList",
                "@id": main_entity_id,
                "name": "Knight Group Handyman Service Categories",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": item["name"],
                        "url": f"{BASE}/Services/{item['slug']}",
                    }
                    for index, item in enumerate(_load("service-catalog.json")["services"])
                ],
            }
        )
    elif page_key == "pricing":
        crumbs.append({"name": "Pricing", "item": f"{BASE}/pricing"})
        main_entity_id = PRICING_CATALOG_ID
        graph.append(pricing_offer_catalog())
    elif page_key == "booking":
        crumbs.append({"name": "Book Estimate", "item": f"{BASE}/booking"})
        page_type = "ContactPage"
        extra["potentialAction"] = {
            "@type": "ContactAction",
            "name": "Request a free handyman estimate",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{BASE}/booking",
                "actionPlatform": [
                    "http://schema.org/DesktopWebPlatform",
                    "http://schema.org/MobileWebPlatform",
                ],
            },
        }
        graph.append(
            service_entity(
                url=f"{BASE}/booking",
                service={
                    "name": "Free handyman estimate request",
                    "serviceType": "Handyman estimate request",
                    "description": meta["description"],
                    "image": "handyman.jpg",
                },
                include_offer_catalog_ref=False,
            )
        )
        main_entity_id = f"{BASE}/booking#service"
    elif page_key == "contact":
        crumbs.append({"name": "Contact", "item": f"{BASE}/contact"})
        page_type = "ContactPage"
        extra["potentialAction"] = {
            "@type": "ContactAction",
            "name": "Contact Knight Group Handyman Services",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{BASE}/contact",
            },
        }
    elif page_key == "about":
        crumbs.append({"name": "About", "item": f"{BASE}/about"})
        page_type = "AboutPage"
        main_entity_id = FOUNDER_ID
    elif page_key == "galleries":
        crumbs.append({"name": "Gallery", "item": f"{BASE}/galleries"})
        manifest = json.loads((ROOT / "GalleryImages" / "gallery-manifest.json").read_text(encoding="utf-8"))
        gallery_nodes = gallery_entities(manifest, meta)
        main_entity_id = f"{BASE}/galleries#gallery"
        graph.extend(gallery_nodes)
    elif page_key == "service-areas":
        crumbs.append({"name": "Service Areas", "item": f"{BASE}/service-areas"})
        page_type = "CollectionPage"
        service = {
            "name": "Tampa Bay handyman service areas",
            "serviceType": "Handyman service areas",
            "description": meta["description"],
            "image": "handyman.jpg",
        }
        graph.append(service_entity(url=url, service=service))
        try:
            from seo_page_data import COUNTY_REGIONS
        except ImportError:
            COUNTY_REGIONS = []
        area_items: list[dict[str, Any]] = []
        position = 1
        for region in COUNTY_REGIONS:
            area_items.append(
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": f"{region['hub_name']} handyman",
                    "url": f"{BASE}/{region['hub_slug']}-handyman",
                }
            )
            position += 1
            for city in region["cities"]:
                area_items.append(
                    {
                        "@type": "ListItem",
                        "position": position,
                        "name": f"{city['name']} handyman",
                        "url": f"{BASE}/{city['slug']}-handyman",
                    }
                )
                position += 1
        list_id = f"{url}#arealist"
        graph.append(
            {
                "@type": "ItemList",
                "@id": list_id,
                "name": "Knight Group Tampa Bay service areas",
                "description": "City and county handyman pages across Pinellas, Hillsborough, and Pasco County.",
                "itemListElement": area_items,
            }
        )
        main_entity_id = list_id
    elif page_key == "geo-county":
        main_entity_id = _append_geo_service_graph(
            graph, url=url, meta=meta, service=service, crumbs=crumbs
        )
        extra["primaryImageOfPage"] = {"@id": f"{url}#primary-image"}
    elif page_key == "geo-city":
        main_entity_id = _append_geo_service_graph(
            graph, url=url, meta=meta, service=service, crumbs=crumbs
        )
        extra["primaryImageOfPage"] = {"@id": f"{url}#primary-image"}
    elif page_key == "geo-combo":
        slug = _url_slug(url)
        city_slug = _combo_city_slug(slug)
        city_label = city_slug.replace("-", " ").title()
        crumbs.extend(
            [
                {"name": "Service Areas", "item": f"{BASE}/service-areas"},
                {"name": f"{city_label} handyman", "item": f"{BASE}/{city_slug}-handyman"},
                {"name": _geo_breadcrumb_label(url, meta, service), "item": url},
            ]
        )
        service_payload = service or {
            "name": meta["title"].split("|")[0].strip(),
            "serviceType": "Handyman services",
            "description": meta["description"],
            "image": "handyman.jpg",
        }
        graph.append(service_entity(url=url, service=service_payload))
        main_entity_id = f"{url}#service"
        image_node = build_image_object(
            image_id=f"{url}#primary-image",
            image_url=f"{BASE}/Images/{service_payload['image']}",
            name=f"{service_payload['name']} photo",
            description=service_payload["description"],
        )
        graph.append(image_node)
        extra["primaryImageOfPage"] = {"@id": image_node["@id"]}
    elif page_key == "geo-handyman":
        main_entity_id = _append_geo_service_graph(
            graph, url=url, meta=meta, service=service, crumbs=crumbs
        )
        extra["primaryImageOfPage"] = {"@id": f"{url}#primary-image"}
    elif page_key == "pricing-niche":
        crumbs.append({"name": "Pricing", "item": f"{BASE}/pricing"})
        crumbs.append({"name": meta["title"].split("|")[0].strip(), "item": url})
        main_entity_id = PRICING_CATALOG_ID
        graph.append(pricing_offer_catalog())
    elif page_key == "gallery-project":
        crumbs.extend(
            [
                {"name": "Gallery", "item": f"{BASE}/galleries"},
                {"name": meta["title"].split("|")[0].strip(), "item": url},
            ]
        )
        project_id = f"{url}#project"
        project_name = meta["title"].split("|")[0].strip()
        project_node: dict[str, Any] = {
            "@type": ["CreativeWork", "ImageGallery"],
            "@id": project_id,
            "name": project_name,
            "description": meta["description"],
            "url": url,
            "provider": {"@id": BUSINESS_ID},
            "about": {"@id": BUSINESS_ID},
            "locationCreated": {
                "@type": "AdministrativeArea",
                "name": "Pinellas County, Florida",
            },
        }
        gallery_image = extract_gallery_project_image(html_content)
        if gallery_image:
            image_url, image_alt = gallery_image
            image_node = build_image_object(
                image_id=f"{url}#primary-image",
                image_url=image_url,
                name=image_alt or project_name,
                description=meta["description"],
            )
            graph.append(image_node)
            project_node["image"] = {"@id": image_node["@id"]}
            extra["primaryImageOfPage"] = {"@id": image_node["@id"]}
        graph.append(project_node)
        main_entity_id = project_id
    elif page_key == "policy":
        label = meta["title"].split("|")[0].strip() if "|" in meta["title"] else "Policy"
        crumbs.append({"name": label, "item": url})
        page_type = "WebPage"
        main_entity_id = BUSINESS_ID
    elif page_key == "service-detail":
        crumbs.extend(
            [
                {"name": "Services", "item": f"{BASE}/services"},
                {"name": service["name"] if service else "Service", "item": url},
            ]
        )
        assert service is not None
        graph.append(service_entity(url=url, service=service))
        main_entity_id = f"{url}#service"
        service_image = build_image_object(
            image_id=f"{url}#primary-image",
            image_url=f"{BASE}/Images/{service['image']}",
            name=f"{service['name']} project photo",
            description=service["description"],
        )
        graph.append(service_image)
        extra["primaryImageOfPage"] = {"@id": service_image["@id"]}
    else:
        raise ValueError(f"Unknown page key: {page_key}")

    graph.append(breadcrumb_entity(url, crumbs))
    graph.append(
        webpage_entity(
            url=url,
            meta=meta,
            page_type=page_type,
            main_entity_id=main_entity_id,
            extra=extra,
        )
    )

    if faq_entities:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{url}#faq",
                "mainEntity": faq_entities,
                "isPartOf": {"@id": f"{url}#webpage"},
            }
        )

    howto = extract_howto(html_content)
    if howto:
        graph.append(
            {
                "@type": "HowTo",
                "@id": f"{url}#howto",
                "name": howto["name"],
                "description": meta["description"],
                "url": url,
                "provider": {"@id": BUSINESS_ID},
                "step": howto["steps"],
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}


def replace_schema_blocks(html: str, graph: dict[str, Any]) -> str:
    graph_json = json.dumps(graph, indent=4, ensure_ascii=False)
    graph_script = (
        '    <!-- JSON-LD entity graph (Organization, LocalBusiness, WebSite, WebPage, page schema) -->\n'
        f'    <script type="application/ld+json">\n{graph_json}\n    </script>\n'
    )
    cleaned = re.sub(
        r"\s*<!--[^>]*Bread\s*Crumbs?[^>]*-->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        html,
        flags=re.S | re.I,
    )
    cleaned = re.sub(
        r"\s*<!--[^>]*(JSON-LD|Structured Data|FAQ Schema)[^>]*-->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        cleaned,
        flags=re.S | re.I,
    )
    cleaned = re.sub(
        r"\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        cleaned,
        count=1,
        flags=re.S | re.I,
    )
    while re.search(r"<script type=\"application/ld\+json\">", cleaned, re.I):
        cleaned = re.sub(
            r"\s*<script type=\"application/ld\+json\">.*?</script>\s*",
            "\n",
            cleaned,
            count=1,
            flags=re.S | re.I,
        )

    anchor = re.search(r"<link rel=\"canonical\"", cleaned, re.I)
    if not anchor:
        anchor = re.search(r"<meta charset", cleaned, re.I)
    if not anchor:
        raise ValueError("Could not find insertion point for JSON-LD")
    pos = anchor.end()
    line_end = cleaned.find("\n", pos)
    if line_end == -1:
        line_end = pos
    return cleaned[: line_end + 1] + "\n" + graph_script + cleaned[line_end + 1 :]


def service_by_slug(slug: str) -> dict[str, str]:
    for item in _load("service-catalog.json")["services"]:
        if item["slug"] == slug:
            return item
    raise KeyError(slug)
