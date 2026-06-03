#!/usr/bin/env python3
"""Upgrade Knight Group service page JSON-LD to full @graph (WebSite, WebPage, Service, FAQPage)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ROOT / "Services"

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
    {"@type": "AdministrativeArea", "name": "Pinellas County, FL"},
]

SKIP = {"programming&databases.html", "handcraftedfurniture&resins.html"}


def extract_meta(html: str) -> dict[str, str]:
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html, re.I)
    canonical = re.search(r'<link rel="canonical" href="([^"]*)"', html, re.I)
    return {
        "title": title.group(1).strip() if title else "",
        "description": desc.group(1).strip() if desc else "",
        "canonical": canonical.group(1).strip() if canonical else "",
    }


def extract_service_block(html: str) -> dict:
    m = re.search(
        r'"@type":\s*"Service"[^}]*?"name":\s*"([^"]+)"[^}]*?"description":\s*"([^"]*)"',
        html,
        re.S,
    )
    if m:
        return {"name": m.group(1), "description": m.group(2)}
    return {"name": "Handyman Services", "description": ""}


def extract_faq(html: str) -> list[dict]:
    m = re.search(
        r'<script type="application/ld\+json">\s*(\{\s*"@context":\s*"https://schema.org",\s*"@type":\s*"FAQPage".*?\})\s*</script>',
        html,
        re.S,
    )
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        return data.get("mainEntity", [])
    except json.JSONDecodeError:
        return []


def breadcrumb_name_from_path(canonical: str) -> str:
    slug = canonical.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").title()


def build_graph(meta: dict, service: dict, faq_entities: list[dict]) -> dict:
    url = meta["canonical"]
    slug = url.rstrip("/").split("/")[-1]
    crumb_label = service["name"] if service["name"] else breadcrumb_name_from_path(url)

    graph: list[dict] = [
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
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://www.knightgroup.com/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Services",
                    "item": "https://www.knightgroup.com/services",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": crumb_label,
                    "item": url,
                },
            ],
        },
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": meta["title"],
            "description": meta["description"],
            "isPartOf": {"@id": "https://www.knightgroup.com/#website"},
            "about": {"@id": "https://www.knightgroup.com/#business"},
            "breadcrumb": {"@id": f"{url}#breadcrumb"},
        },
        {
            "@type": "Service",
            "@id": f"{url}#service",
            "name": service["name"],
            "description": service["description"],
            "provider": {"@id": "https://www.knightgroup.com/#business"},
            "url": url,
            "serviceType": service["name"],
            "areaServed": AREA_SERVED,
        },
    ]

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


def replace_schema(html: str, graph: dict) -> str:
    graph_json = json.dumps(graph, indent=4, ensure_ascii=False)
    graph_script = (
        '    <!-- JSON-LD Structured Data (WebSite, WebPage, Service, FAQPage) -->\n'
        f'    <script type="application/ld+json">\n{graph_json}\n    </script>\n'
    )

    html = re.sub(
        r"\s*<!--\s*Bread\s*Crumbs?\s*-->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        html,
        count=1,
        flags=re.S | re.I,
    )
    html = re.sub(
        r"\s*<!-- JSON-LD Structured Data -->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r"\s*<!-- FAQ Schema -->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
        "\n",
        html,
        count=1,
        flags=re.S,
    )

    insert_at = re.search(r"<style>\*", html)
    if not insert_at:
        insert_at = re.search(r"<style>", html)
    if not insert_at:
        raise ValueError("Could not find style block for schema insertion")

    pos = insert_at.start()
    return html[:pos] + graph_script + "\n" + html[pos:]


def main() -> None:
    updated = 0
    for path in sorted(SERVICES.glob("*.html")):
        if path.name in SKIP:
            print("skip", path.name)
            continue
        html = path.read_text(encoding="utf-8")
        meta = extract_meta(html)
        if not meta["canonical"]:
            print("no canonical", path.name)
            continue
        service = extract_service_block(html)
        faq = extract_faq(html)
        graph = build_graph(meta, service, faq)
        new_html = replace_schema(html, graph)
        if new_html != html:
            path.write_text(new_html, encoding="utf-8")
            updated += 1
            print("updated", path.name)
    print(f"Done. {updated} service pages updated.")


if __name__ == "__main__":
    main()
