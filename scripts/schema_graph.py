#!/usr/bin/env python3
"""Build unified JSON-LD @graph blocks for Knight Group canonical pages."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEO = ROOT / "seo"
BASE = "https://www.knightgroup.com"
BUSINESS_ID = f"{BASE}/#business"
ORG_ID = f"{BASE}/#organization"
FOUNDER_ID = f"{BASE}/#founder"
WEBSITE_ID = f"{BASE}/#website"
PRICING_CATALOG_ID = f"{BASE}/pricing#offer-catalog"

AREA_SERVED = [
    {"@type": "City", "name": "Safety Harbor, FL"},
    {"@type": "City", "name": "Clearwater, FL"},
    {"@type": "City", "name": "Dunedin, FL"},
    {"@type": "City", "name": "Palm Harbor, FL"},
    {"@type": "City", "name": "Largo, FL"},
    {"@type": "City", "name": "Oldsmar, FL"},
    {"@type": "City", "name": "Tarpon Springs, FL"},
    {"@type": "City", "name": "Seminole, FL"},
    {"@type": "City", "name": "St. Petersburg, FL"},
    {"@type": "AdministrativeArea", "name": "Pinellas County, Florida"},
]

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


def business_entity(*, include_reviews: bool = False) -> dict[str, Any]:
    entity = copy.deepcopy(_load("knight-group-business-entity.json"))
    if include_reviews:
        entity["review"] = _load("knight-group-reviews-home.json")
    return entity


def website_entity() -> dict[str, Any]:
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": f"{BASE}/",
        "name": "Knight Group Handyman Services",
        "description": "Registered and insured handyman services in Safety Harbor and Pinellas County, Florida.",
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


def service_entity(
    *,
    url: str,
    service: dict[str, str],
    include_offer_catalog_ref: bool = True,
) -> dict[str, Any]:
    image = f"{BASE}/Images/{service['image']}"
    node: dict[str, Any] = {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": service["name"],
        "description": service["description"],
        "serviceType": service["serviceType"],
        "provider": {"@id": BUSINESS_ID},
        "url": url,
        "image": image,
        "areaServed": AREA_SERVED,
        "offers": {
            "@type": "Offer",
            "url": f"{BASE}/booking",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "eligibleRegion": {
                "@type": "AdministrativeArea",
                "name": "Pinellas County, Florida",
            },
        },
    }
    if include_offer_catalog_ref:
        node["hasOfferCatalog"] = {"@id": PRICING_CATALOG_ID}
    return node


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
                "description": "Common handyman repairs, punch-list work, fixture swaps, caulking, sealing, and small drywall patches.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": {
                    "@type": "Service",
                    "name": "Standard handyman visit",
                    "serviceType": "Handyman services",
                    "provider": {"@id": BUSINESS_ID},
                },
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
                "description": "Handyman-level faucet, shutoff, fixture, and small leak repairs — not licensed plumbing contractor work.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": {
                    "@type": "Service",
                    "name": "Minor plumbing repair visit",
                    "serviceType": "Handyman plumbing fixture repair",
                    "provider": {"@id": BUSINESS_ID},
                },
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
                "itemOffered": {
                    "@type": "Service",
                    "name": "Specialty install and repair visit",
                    "serviceType": "Specialty handyman work",
                    "provider": {"@id": BUSINESS_ID},
                },
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
                "name": "Emergency service call",
                "description": "Urgent after-hours, weekend, or holiday handyman response with a one-time emergency fee added to the applicable hourly rate.",
                "url": f"{BASE}/pricing",
                "priceCurrency": "USD",
                "itemOffered": {
                    "@type": "Service",
                    "name": "Emergency service call",
                    "serviceType": "Emergency handyman repairs",
                    "provider": {"@id": BUSINESS_ID},
                },
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
        image_node = {
            "@type": "ImageObject",
            "@id": image_id,
            "url": image_url,
            "contentUrl": image_url,
            "name": image.get("title") or group["title"],
            "description": image.get("description") or group["description"],
            "creator": {"@id": BUSINESS_ID},
        }
        project_node = {
            "@type": "CreativeWork",
            "@id": project_id,
            "name": group["title"],
            "description": group["description"],
            "about": {
                "@type": "Service",
                "name": group.get("category", "Handyman project"),
                "provider": {"@id": BUSINESS_ID},
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
    return [gallery, *image_nodes, *project_nodes]


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
) -> dict[str, Any]:
    url = meta["canonical"].rstrip("/")
    if page_key == "home":
        url = f"{BASE}/"
    graph = base_graph(include_reviews=True)
    crumbs = [{"name": "Home", "item": f"{BASE}/"}]
    main_entity_id: str | None = BUSINESS_ID
    page_type = "WebPage"
    extra: dict[str, Any] = {
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": f"{BASE}/Images/KGHero.webp",
        }
    }

    if page_key == "home":
        pass
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
        service = {
            "name": "Pinellas County handyman service areas",
            "serviceType": "Handyman service areas",
            "description": meta["description"],
            "image": "handyman.jpg",
        }
        graph.append(service_entity(url=url, service=service))
        main_entity_id = f"{url}#service"
    elif page_key == "geo-handyman":
        label = "Pinellas Handyman" if url.endswith("/pinellas-handyman") else "Clearwater Handyman"
        crumbs.extend(
            [
                {"name": "Service Areas", "item": f"{BASE}/service-areas"},
                {"name": label, "item": url},
            ]
        )
        service = service or {
            "name": label,
            "serviceType": "Handyman services",
            "description": meta["description"],
            "image": "handyman.jpg",
        }
        graph.append(service_entity(url=url, service=service))
        main_entity_id = f"{url}#service"
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
        extra["primaryImageOfPage"] = {
            "@type": "ImageObject",
            "url": f"{BASE}/Images/{service['image']}",
        }
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
