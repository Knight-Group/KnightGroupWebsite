#!/usr/bin/env python3
"""Inject unified JSON-LD entity graphs across Knight Group canonical pages."""

from __future__ import annotations

from pathlib import Path

from schema_graph import (
    build_graph_for_page,
    extract_faq_entities,
    extract_meta,
    replace_schema_blocks,
    service_by_slug,
)

ROOT = Path(__file__).resolve().parents[1]
SKIP_SERVICES = {"programming&databases.html", "handcraftedfurniture&resins.html", "index.html"}

PAGE_MAP: list[tuple[str, str, dict | None]] = [
    ("index.html", "home", None),
    ("services.html", "services-hub", None),
    ("pricing.html", "pricing", None),
    ("booking.html", "booking", None),
    ("contact.html", "contact", None),
    ("about.html", "about", None),
    ("galleries.html", "galleries", None),
    ("service-areas.html", "service-areas", None),
    (
        "pinellas-handyman.html",
        "geo-handyman",
        {
            "name": "Handyman services in Pinellas County",
            "serviceType": "Handyman services in Pinellas County",
            "description": "Handyman company serving Pinellas County with repairs, drywall, plumbing fixture work, painting, carpentry, and punch-list projects.",
            "image": "handyman.jpg",
        },
    ),
    (
        "clearwater-handyman.html",
        "geo-handyman",
        {
            "name": "Clearwater handyman services",
            "serviceType": "Clearwater handyman services",
            "description": "Local handyman services for Clearwater homeowners including fixture swaps, drywall repair, painting touch-ups, and general home repairs.",
            "image": "handyman.jpg",
        },
    ),
]


def update_file(path: Path, page_key: str, service: dict | None = None) -> bool:
    html = path.read_text(encoding="utf-8")
    meta = extract_meta(html)
    if not meta["canonical"]:
        print(f"skip (no canonical): {path.name}")
        return False
    faq = extract_faq_entities(html)
    graph = build_graph_for_page(
        page_key=page_key,
        meta=meta,
        faq_entities=faq,
        service=service,
    )
    updated = replace_schema_blocks(html, graph)
    if updated == html:
        print(f"no change: {path.relative_to(ROOT)}")
        return False
    path.write_text(updated, encoding="utf-8")
    print(f"updated: {path.relative_to(ROOT)}")
    return True


def main() -> int:
    changed = 0
    for rel_path, page_key, service in PAGE_MAP:
        if update_file(ROOT / rel_path, page_key, service=service):
            changed += 1

    for path in sorted((ROOT / "Services").glob("*.html")):
        if path.name in SKIP_SERVICES:
            continue
        slug = path.stem
        try:
            service = service_by_slug(slug)
        except KeyError:
            print(f"skip (no catalog entry): {path.name}")
            continue
        if update_file(path, "service-detail", service=service):
            changed += 1

    print(f"Done. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
