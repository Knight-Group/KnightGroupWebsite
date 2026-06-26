#!/usr/bin/env python3
"""Rebuild seo/meta-descriptions.json from Serper research + geo SEO copy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from geo_seo_copy import city_copy, combo_copy, county_copy  # noqa: E402
from serp_query_map import build_full_page_query_map  # noqa: E402

ROOT = SCRIPT_DIR.parent
SEO = ROOT / "seo"
SERP_PATH = SEO / "serp-meta-research.json"
OUT_PATH = SEO / "meta-descriptions.json"
MAX_LEN = 159

POLICY_PAGES = [
    {
        "path": "PolicyPages/privacy-policy.html",
        "description": "Knight Group privacy policy for handyman services in Safety Harbor and Tampa Bay, Florida.",
    },
    {
        "path": "PolicyPages/terms.html",
        "description": "Knight Group terms of service for handyman repairs and projects in Safety Harbor and Tampa Bay, Florida.",
    },
    {
        "path": "PolicyPages/payment-policy.html",
        "description": "Knight Group payment policy: billing terms and accepted methods for Tampa Bay handyman work.",
    },
    {
        "path": "PolicyPages/returnpolicy.html",
        "description": "Knight Group 30-day workmanship guarantee for handyman services in Safety Harbor and Tampa Bay, Florida.",
    },
]


def clip(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= MAX_LEN:
        return text
    return text[: MAX_LEN - 3].rstrip() + "..."


def geo_override(path: str) -> str | None:
    if path.endswith("-handyman.html"):
        slug = path.removesuffix("-handyman.html")
        if slug in {"pinellas", "hillsborough", "pasco"}:
            return str(county_copy(slug).get("meta_description") or "")
        return str(city_copy(slug).get("meta_description") or "")
    if (
        path.endswith(".html")
        and not path.startswith(("Services/", "pricing-", "PolicyPages/", "gallery/"))
        and path not in {"index.html", "about.html", "contact.html", "booking.html", "services.html", "pricing.html", "galleries.html", "service-areas.html"}
    ):
        slug = path.removesuffix(".html")
        copy = combo_copy(slug)
        if copy.get("meta_description"):
            return str(copy["meta_description"])
    return None


def best_serp_description(serp_rows: list[dict], page_path: str) -> tuple[str, list[str], str]:
    matches = [row for row in serp_rows if row.get("target_page") == page_path and not row.get("error")]
    queries = [str(row.get("query") or "") for row in matches]
    if not matches:
        return "", queries, ""
    ranked = sorted(
        matches,
        key=lambda row: (
            0 if row.get("knightgroup_rank") else 1,
            -(int(row.get("gsc_impressions") or 0) if str(row.get("gsc_impressions") or "").isdigit() else 0),
        ),
    )
    primary = ranked[0]
    suggested = str(primary.get("suggested_meta_description") or "").strip()
    note_parts = []
    for row in ranked[:2]:
        competitors = row.get("competitor_title_angles") or []
        if competitors:
            note_parts.append(f"{row.get('query')}: compete with {competitors[0]}")
    return clip(suggested), queries, "; ".join(note_parts)


def legacy_fallback(path: str) -> str:
    fallbacks = {
        "index.html": "Knight Group Handyman Services in Safety Harbor & Tampa Bay. Repairs, plumbing, drywall & paint. Free estimate.",
        "services.html": "Handyman services in Tampa Bay: repairs, plumbing, electrical, carpentry, painting, doors, windows & more.",
        "service-areas.html": "Handyman service areas across Pinellas, Hillsborough & Pasco County. Safety Harbor HQ. Confirm your city.",
    }
    return fallbacks.get(path, "")


def main() -> int:
    if not SERP_PATH.exists():
        print("Run scripts/serp-meta-research.py first.")
        return 1

    serp = json.loads(SERP_PATH.read_text(encoding="utf-8"))
    serp_rows = list(serp.get("results") or [])
    page_map = build_full_page_query_map()

    pages: list[dict] = []
    for page_path in sorted(page_map.keys()):
        override = geo_override(page_path)
        description, queries, note = best_serp_description(serp_rows, page_path)
        if override:
            description = clip(override)
        elif not description:
            description = clip(legacy_fallback(page_path))
        if not description:
            continue
        pages.append(
            {
                "path": page_path,
                "gsc_queries": queries,
                "serper_note": note,
                "description": description,
            }
        )

    pages = [entry for entry in pages if (ROOT / entry["path"]).is_file()]
    pages.extend(POLICY_PAGES)

    payload = {
        "serper_research": "seo/serp-meta-research.json",
        "serper_generated_at": serp.get("generated_at"),
        "pages": pages,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(pages)} meta entries to {OUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
