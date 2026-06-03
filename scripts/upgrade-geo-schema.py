#!/usr/bin/env python3
"""Upgrade clearwater-handyman and pinellas-handyman JSON-LD graphs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    {
        "file": "clearwater-handyman.html",
        "url": "https://www.knightgroup.com/clearwater-handyman",
        "title": "Clearwater Handyman | Home & Sink Repairs | Knight Group",
        "description": "Clearwater handyman for sink repairs, fixtures, drywall, painting & punch-list work. Knight Group serves Pinellas County from Safety Harbor. Free estimate: (813) 649-3341.",
        "service_name": "Clearwater handyman services",
        "service_type": "Handyman repairs, sink and fixture work, drywall, painting, carpentry",
        "crumb": "Clearwater Handyman",
        "faq": [
            {
                "@type": "Question",
                "name": "Does Knight Group offer handyman service in Clearwater, FL?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Knight Group regularly routes handyman and home repair work to Clearwater and nearby Pinellas County neighborhoods from its Safety Harbor base.",
                },
            },
            {
                "@type": "Question",
                "name": "Can Knight Group handle sink repair in Clearwater?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. For leaking sinks, faucet swaps, shutoff issues, and related fixture work in Clearwater, use the plumbing services page or call (813) 649-3341 for a free estimate.",
                },
            },
        ],
    },
    {
        "file": "pinellas-handyman.html",
        "url": "https://www.knightgroup.com/pinellas-handyman",
        "title": "Handyman Pinellas County FL | Knight Group Handyman Company",
        "description": "Handyman company in Pinellas County FL — Safety Harbor, Clearwater, Dunedin, Palm Harbor & Largo. Repairs, drywall, plumbing & painting. Free estimates: (813) 649-3341.",
        "service_name": "Handyman services in Pinellas County",
        "service_type": "Handyman repairs, home maintenance, drywall, plumbing fixtures, painting, carpentry",
        "crumb": "Pinellas Handyman",
        "faq": [
            {
                "@type": "Question",
                "name": "Who is a handyman company that serves Pinellas County?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Knight Group Handyman Services LLC is a registered and insured handyman business based in Safety Harbor with regular routes across Pinellas County.",
                },
            },
            {
                "@type": "Question",
                "name": "What types of handyman jobs does Knight Group handle in Pinellas County?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Knight Group handles punch-list repairs, fixture swaps, drywall and paint work, trim and carpentry fixes, door and window adjustments, and smaller renovation projects with free written estimates.",
                },
            },
        ],
    },
]

AREA_SERVED = [
    {"@type": "City", "name": "Safety Harbor, FL"},
    {"@type": "City", "name": "Clearwater, FL"},
    {"@type": "City", "name": "Dunedin, FL"},
    {"@type": "City", "name": "Palm Harbor, FL"},
    {"@type": "City", "name": "Largo, FL"},
    {"@type": "AdministrativeArea", "name": "Pinellas County, FL"},
]


def build_graph(page: dict) -> dict:
    url = page["url"]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": "https://www.knightgroup.com/#website",
                "url": "https://www.knightgroup.com/",
                "name": "Knight Group Handyman Services",
                "publisher": {"@id": "https://www.knightgroup.com/#business"},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.knightgroup.com/"},
                    {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url},
                ],
            },
            {
                "@type": "WebPage",
                "@id": f"{url}#webpage",
                "url": url,
                "name": page["title"],
                "description": page["description"],
                "isPartOf": {"@id": "https://www.knightgroup.com/#website"},
                "about": {"@id": "https://www.knightgroup.com/#business"},
                "breadcrumb": {"@id": f"{url}#breadcrumb"},
            },
            {
                "@type": "Service",
                "@id": f"{url}#service",
                "name": page["service_name"],
                "serviceType": page["service_type"],
                "provider": {"@id": "https://www.knightgroup.com/#business"},
                "url": url,
                "areaServed": AREA_SERVED,
            },
            {
                "@type": "FAQPage",
                "@id": f"{url}#faq",
                "mainEntity": page["faq"],
                "isPartOf": {"@id": f"{url}#webpage"},
            },
        ],
    }


def main() -> None:
    for page in PAGES:
        path = ROOT / page["file"]
        html = path.read_text(encoding="utf-8")
        graph = build_graph(page)
        graph_json = json.dumps(graph, indent=4, ensure_ascii=False)
        new_block = f'    <script type="application/ld+json">\n{graph_json}\n    </script>'
        html = re.sub(
            r'<script type="application/ld\+json">.*?</script>',
            new_block,
            html,
            count=1,
            flags=re.S,
        )
        path.write_text(html, encoding="utf-8")
        print("updated", page["file"])


if __name__ == "__main__":
    main()
