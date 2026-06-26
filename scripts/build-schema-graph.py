#!/usr/bin/env python3
"""Inject unified JSON-LD entity graphs across all Knight Group canonical pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_graph import (  # noqa: E402
    build_graph_for_page,
    extract_meta,
    extract_page_faq,
    replace_schema_blocks,
    service_by_slug,
)
from seo_page_data import NICHE_SERVICES  # noqa: E402

ROOT = SCRIPT_DIR.parent
SEO = ROOT / "seo"
MANIFEST = SEO / "page-manifest.json"
SKIP_SERVICES = {"programming&databases.html", "handcraftedfurniture&resins.html", "index.html"}

CORE_PAGES: list[tuple[str, str]] = [
    ("index.html", "home"),
    ("services.html", "services-hub"),
    ("pricing.html", "pricing"),
    ("booking.html", "booking"),
    ("contact.html", "contact"),
    ("about.html", "about"),
    ("galleries.html", "galleries"),
    ("service-areas.html", "service-areas"),
]

POLICY_PAGES = [
    "PolicyPages/privacy-policy.html",
    "PolicyPages/terms.html",
    "PolicyPages/payment-policy.html",
    "PolicyPages/returnpolicy.html",
]

NICHE_BY_SLUG = {item["slug"]: item for item in NICHE_SERVICES}

PAGE_TYPE_TO_KEY = {
    "county": "geo-county",
    "city": "geo-city",
    "city-service": "geo-combo",
    "pricing-niche": "pricing-niche",
    "gallery-project": "gallery-project",
    "niche-service": "service-detail",
}


def niche_service_payload(defn: dict, description: str) -> dict[str, str]:
    hero = defn.get("hero", "handyman.webp")
    return {
        "name": defn["h1"],
        "serviceType": defn["h1"],
        "description": description,
        "image": hero.replace(".webp", ".jpg"),
    }


def service_from_html(path: Path, meta: dict[str, str]) -> dict[str, str] | None:
    slug = path.stem
    try:
        return service_by_slug(slug)
    except KeyError:
        pass
    if slug in NICHE_BY_SLUG:
        return niche_service_payload(NICHE_BY_SLUG[slug], meta["description"])
    return None


def update_file(path: Path, page_key: str, service: dict[str, str] | None = None) -> bool:
    if not path.is_file():
        print(f"skip (missing): {path.relative_to(ROOT)}")
        return False
    html = path.read_text(encoding="utf-8")
    meta = extract_meta(html)
    if not meta["canonical"]:
        print(f"skip (no canonical): {path.name}")
        return False
    faq = extract_page_faq(html)
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

    for rel_path, page_key in CORE_PAGES:
        if update_file(ROOT / rel_path, page_key):
            changed += 1

    for rel_path in POLICY_PAGES:
        if update_file(ROOT / rel_path, "policy"):
            changed += 1

    for path in sorted((ROOT / "Services").glob("*.html")):
        if path.name in SKIP_SERVICES:
            continue
        html = path.read_text(encoding="utf-8")
        meta = extract_meta(html)
        service = service_from_html(path, meta)
        if not service:
            print(f"skip (no service payload): {path.name}")
            continue
        if update_file(path, "service-detail", service=service):
            changed += 1

    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for entry in manifest.get("pages", []):
            page_type = entry.get("pageType", "")
            page_key = PAGE_TYPE_TO_KEY.get(page_type)
            if not page_key:
                continue
            rel_path = entry["path"]
            path = ROOT / rel_path
            service = None
            if page_type in {"city", "county", "city-service", "niche-service"}:
                html = path.read_text(encoding="utf-8") if path.is_file() else ""
                meta = extract_meta(html) if html else {"description": ""}
                slug = entry.get("slug", path.stem)
                if page_type == "niche-service" and slug in NICHE_BY_SLUG:
                    service = niche_service_payload(NICHE_BY_SLUG[slug], meta.get("description", ""))
                elif page_type in {"city", "county", "city-service"}:
                    service = {
                        "name": meta.get("title", slug).split("|")[0].strip(),
                        "serviceType": "Handyman services",
                        "description": meta.get("description", ""),
                        "image": "handyman.jpg",
                    }
            if update_file(path, page_key, service=service):
                changed += 1

    print(f"Done. {changed} pages updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
