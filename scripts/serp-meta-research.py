#!/usr/bin/env python3
"""Run Serper.dev SERP research for Knight Group meta description work."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
SEO = ROOT / "seo"
OUTREACH_ENV = Path(r"E:\KnightLogics-Growth-System\CRM\OutreachEngine\.env")
GSC_QUERIES = ROOT / "gsc-export-2026-06-03" / "Queries.csv"
META_CONFIG = SEO / "meta-descriptions.json"
SERPER_ENDPOINT = "https://google.serper.dev/search"
SITE_DOMAIN = "knightgroup.com"
DEFAULT_LOCATION = "Pinellas County, Florida, United States"

PAGE_QUERY_MAP: dict[str, list[str]] = {
    "index.html": ["knight group", "knightgroup", "handyman pinellas county"],
    "Services/handyman.html": [
        "handyman company pinellas",
        "handyman pinellas county fl",
        "handyman near me small jobs",
    ],
    "Services/plumbing-services.html": [
        "sink repair clearwater",
        "plumbing services in pinellas county",
        "plumbing repair clearwater fl",
    ],
    "about.html": ["knight group handyman", "knight services llc", "knights handyman services"],
    "contact.html": ["knight group handyman contact"],
    "booking.html": ["handyman estimate pinellas county"],
    "Services/general-repairs.html": ["handyman pinellas county", "general home repairs pinellas"],
    "galleries.html": ["handyman projects pinellas county"],
    "service-areas.html": ["handyman service areas pinellas county"],
    "pinellas-handyman.html": ["handyman pinellas county", "handyman company pinellas"],
    "clearwater-handyman.html": ["sink repair clearwater", "clearwater handyman"],
    "services.html": ["handyman services pinellas county"],
    "pricing.html": ["handyman prices pinellas county", "handyman near me prices"],
    "Services/carpentry-framing.html": ["carpentry services near me", "carpenter pinellas county"],
    "Services/doors-windows.html": ["door repair pinellas county", "window repair clearwater"],
    "Services/electrical-work.html": ["handyman electrical work pinellas county"],
    "Services/emergency-services.html": ["emergency handyman pinellas county"],
    "Services/home-renovations.html": ["small home renovations pinellas county"],
    "Services/painting-finishing.html": ["handyman painting pinellas county"],
    "Services/custom-projects.html": ["custom handyman projects pinellas county"],
}


def load_serper_key() -> str:
    if not OUTREACH_ENV.exists():
        raise RuntimeError(f"Serper env not found: {OUTREACH_ENV}")
    for raw_line in OUTREACH_ENV.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "SERPER_API_KEY":
            token = value.strip().strip('"').strip("'")
            if token:
                return token
    raise RuntimeError("SERPER_API_KEY missing in OutreachEngine/.env")


def normalize_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def load_gsc_queries() -> list[dict[str, str]]:
    if not GSC_QUERIES.exists():
        return []
    rows: list[dict[str, str]] = []
    with GSC_QUERIES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            query = (row.get("Top queries") or "").strip()
            if not query:
                continue
            rows.append(
                {
                    "query": query,
                    "impressions": (row.get("Impressions") or "0").strip(),
                    "position": (row.get("Position") or "").strip(),
                }
            )
    return rows


def collect_queries() -> list[dict[str, Any]]:
    seen: set[str] = set()
    items: list[dict[str, Any]] = []

    def add(query: str, *, page: str, source: str, impressions: str = "") -> None:
        key = query.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        items.append(
            {
                "query": query.strip(),
                "target_page": page,
                "source": source,
                "gsc_impressions": impressions,
            }
        )

    for page, queries in PAGE_QUERY_MAP.items():
        for query in queries:
            add(query, page=page, source="page_map")

    for row in load_gsc_queries():
        query = row["query"]
        page = "index.html"
        for candidate_page, candidate_queries in PAGE_QUERY_MAP.items():
            if query.lower() in {q.lower() for q in candidate_queries}:
                page = candidate_page
                break
        add(query, page=page, source="gsc", impressions=row["impressions"])

    return items


def fetch_serp(api_key: str, query: str, location: str) -> dict[str, Any]:
    response = requests.post(
        SERPER_ENDPOINT,
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={
            "q": query,
            "gl": "us",
            "hl": "en",
            "num": 10,
            "location": location,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def summarize_organic(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(data.get("organic") or [], start=1):
        if not isinstance(item, dict):
            continue
        link = str(item.get("link") or "")
        rows.append(
            {
                "position": index,
                "title": item.get("title"),
                "link": link,
                "domain": normalize_domain(link),
                "snippet": item.get("snippet"),
                "is_knightgroup": SITE_DOMAIN in normalize_domain(link),
            }
        )
    return rows


def summarize_places(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("places") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "title": item.get("title"),
                "address": item.get("address"),
                "rating": item.get("rating"),
                "ratingCount": item.get("ratingCount"),
                "phone": item.get("phoneNumber"),
                "website": item.get("website"),
            }
        )
    return rows


def infer_intent(query: str, organic: list[dict[str, Any]], places: list[dict[str, Any]]) -> str:
    q = query.lower()
    if places:
        return "local_service_map_pack"
    if any(token in q for token in ("price", "cost", "estimate", "quote")):
        return "pricing_estimate"
    if any(token in q for token in ("knight group", "knightgroup", "knight services")):
        return "brand_navigational"
    if "near me" in q or "pinellas" in q or "clearwater" in q or "safety harbor" in q:
        return "local_service"
    domains = {row["domain"] for row in organic[:5]}
    if any("bbb.org" in d or "yelp." in d for d in domains):
        return "local_directory_mix"
    return "general_service"


def main() -> int:
    api_key = load_serper_key()
    queries = collect_queries()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    results: list[dict[str, Any]] = []

    for item in queries:
        query = item["query"]
        try:
            data = fetch_serp(api_key, query, DEFAULT_LOCATION)
        except requests.RequestException as exc:
            results.append({**item, "error": str(exc)})
            print(f"ERROR {query}: {exc}")
            continue

        organic = summarize_organic(data)
        places = summarize_places(data)
        knight_hit = next((row for row in organic if row["is_knightgroup"]), None)
        top_competitors = [row for row in organic[:5] if not row["is_knightgroup"]]

        payload = {
            **item,
            "location": DEFAULT_LOCATION,
            "intent": infer_intent(query, organic, places),
            "knightgroup_rank": knight_hit["position"] if knight_hit else None,
            "knightgroup_result": knight_hit,
            "top_competitors": top_competitors,
            "competitor_title_angles": [row.get("title") for row in top_competitors[:3]],
            "competitor_snippet_angles": [row.get("snippet") for row in top_competitors[:3]],
            "map_pack": places[:3],
            "people_also_ask": [
                row.get("question")
                for row in (data.get("peopleAlsoAsk") or [])
                if isinstance(row, dict) and row.get("question")
            ][:3],
            "search_information": data.get("searchInformation"),
        }
        results.append(payload)
        rank = payload["knightgroup_rank"]
        print(f"OK   {query} -> rank {rank if rank else 'not in top 10'}")

    report = {
        "generated_at": generated_at,
        "location_default": DEFAULT_LOCATION,
        "query_count": len(results),
        "results": results,
    }
    json_path = SEO / "serp-meta-research.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        "# Knight Group Serper meta research",
        f"Generated: {generated_at}",
        f"Location: {DEFAULT_LOCATION}",
        "",
    ]
    for row in results:
        md_lines.append(f"## {row['query']}")
        md_lines.append(f"- Target page: `{row.get('target_page', '')}`")
        md_lines.append(f"- GSC impressions: {row.get('gsc_impressions') or 'n/a'}")
        md_lines.append(f"- Intent: {row.get('intent', 'n/a')}")
        md_lines.append(f"- Knight Group rank: {row.get('knightgroup_rank') or 'not in top 10'}")
        if row.get("knightgroup_result"):
            hit = row["knightgroup_result"]
            md_lines.append(f"- Current title: {hit.get('title')}")
            md_lines.append(f"- Current snippet: {hit.get('snippet')}")
        if row.get("top_competitors"):
            md_lines.append("- Top competitors:")
            for comp in row["top_competitors"][:3]:
                md_lines.append(f"  - {comp.get('title')} | {comp.get('domain')}")
        if row.get("map_pack"):
            md_lines.append("- Map pack:")
            for place in row["map_pack"]:
                md_lines.append(f"  - {place.get('title')} ({place.get('rating')})")
        if row.get("error"):
            md_lines.append(f"- Error: {row['error']}")
        md_lines.append("")

    md_path = SEO / "serp-meta-research.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nWrote {json_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
