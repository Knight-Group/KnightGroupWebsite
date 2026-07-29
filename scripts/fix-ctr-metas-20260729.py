#!/usr/bin/env python3
"""2026-07-29 CTR + indexing cleanup for Knight Group.

Fixes Serper-scraped competitor metas, keyword-stuffed geo snippets,
money-page titles for high-impression queries, and removes llms.txt from sitemap.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from page_meta import clip_meta  # noqa: E402

META_PATH = ROOT / "seo" / "meta-descriptions.json"

# High-impression / quick-win title overrides (GSC 2026-07-18).
TITLE_OVERRIDES: dict[str, str] = {
    "Services/handyman.html": "Handyman Near Me | Pinellas County FL | No 2-Hour Minimum",
    "Services/home-repair-near-me.html": "Home Repair Near Me | Pinellas County FL | Free Estimate",
    "Services/small-job-carpenter.html": "Small Job Carpenter Near Me | Pinellas County | Knight Group",
    "Services/doors-windows.html": "Door & Window Repair Near Me | Pinellas County FL",
    "Services/general-repairs.html": "General Home Repairs | Pinellas County | No 2-Hour Minimum",
    "pricing.html": "Handyman Pricing | $75/hr · No 2-Hour Minimum | Pinellas FL",
    "clearwater-handyman.html": "Clearwater Handyman Near You | Free Estimate | Knight Group",
    "largo-handyman.html": "Largo Handyman | Free Estimate | Call (813) 649-3341",
    "temple-terrace-handyman.html": "Temple Terrace Handyman | Free Estimate | Knight Group",
    "hillsborough-handyman.html": "Hillsborough County Handyman | Tampa Bay | Free Estimate",
    "pinellas-handyman.html": "Pinellas County Handyman | Local Crew | Free Estimate",
    "tampa-handyman.html": "Tampa Handyman | Hillsborough County | Free Estimate",
    "services.html": "Handyman Services | Pinellas County FL | Knight Group",
}

# Clean conversion-focused metas for polluted / stuffed pages.
META_OVERRIDES: dict[str, str] = {
    "Services/home-repair-near-me.html": (
        "Home repair near you in Pinellas County: drywall, doors, fixture plumbing, paint, and "
        "punch-list fixes. Registered Safety Harbor crew. No 2-hour minimum. Free written estimate."
    ),
    "Services/small-job-carpenter.html": (
        "Small-job carpenter in Pinellas County for trim, shelves, door frames, and wood repairs. "
        "Registered and insured. No 2-hour minimum. Free written estimate."
    ),
    "Services/door-adjustment.html": (
        "Door adjustment and sticking-door repair in Pinellas County: hinges, latches, sweeps, and "
        "alignment. Registered and insured. Free written estimate."
    ),
    "Services/doors-windows.html": (
        "Door and window repair in Pinellas County: sticking doors, locks, screens, weatherstripping, "
        "and small window fixes. Registered and insured. Free written estimate."
    ),
    "Services/drain-unclogging.html": (
        "Handyman drain unclogging in Pinellas County for sinks, tubs, and fixture-level clogs. "
        "Registered and insured. Call (813) 649-3341 for active backups."
    ),
    "Services/interior-painting.html": (
        "Interior painting and touch-ups in Pinellas County: rooms, trim, stain blocking, and "
        "paint-ready drywall repair. Registered and insured. Free written estimate."
    ),
    "Services/cabinet-repair.html": (
        "Cabinet repair in Pinellas County: hinges, doors, drawers, hardware, and touch-up finishing. "
        "Registered and insured. Free written estimate."
    ),
    "Services/custom-projects.html": (
        "Custom handyman projects in Pinellas County: built-ins, shelving, accent walls, and one-off "
        "home improvements. Registered and insured. Free written estimate."
    ),
    "Services/custom-shelving.html": (
        "Custom shelving install and repair in Pinellas County: closets, garages, and display shelves. "
        "Registered and insured. Free written estimate."
    ),
    "Services/handyman.html": (
        "Local Pinellas County handyman near you for drywall, plumbing fixtures, doors, paint, and "
        "punch lists. From $75/hr with no 2-hour minimum. Free written estimate."
    ),
    "pricing.html": (
        "Handyman pricing in Pinellas County: $150 first hour, $75 after with no 2-hour minimum. "
        "Compare visit packages and request a free written estimate today."
    ),
    "clearwater-handyman.html": (
        "Clearwater handyman for drywall, fixture plumbing, doors, and punch-list repairs. Local "
        "Safety Harbor crew — registered and insured. Free written estimate."
    ),
    "largo-handyman.html": (
        "Largo handyman for drywall, fixture plumbing, doors, and punch-list repairs. Registered and "
        "insured Safety Harbor crew. Free written estimate. Call (813) 649-3341."
    ),
    "temple-terrace-handyman.html": (
        "Temple Terrace handyman for drywall, carpentry, doors, fixture plumbing, and punch lists. "
        "Registered and insured. Free written estimate. Call (813) 649-3341."
    ),
    "hillsborough-handyman.html": (
        "Hillsborough County handyman covering Tampa Bay neighborhoods for drywall, doors, fixture "
        "plumbing, and punch lists. Registered and insured. Free written estimate."
    ),
    "pinellas-handyman.html": (
        "Pinellas County handyman company for drywall, fixture plumbing, doors, paint, and punch-list "
        "repairs. Local Safety Harbor crew. Free written estimate."
    ),
    "tampa-handyman.html": (
        "Tampa handyman for drywall, doors, fixture plumbing, and punch-list repairs across "
        "Hillsborough County routes. Registered and insured. Free written estimate."
    ),
    "dunedin-handyman.html": (
        "Dunedin handyman for drywall, fixture plumbing, doors, and punch-list repairs. Registered "
        "and insured Safety Harbor crew. Free written estimate."
    ),
    "oldsmar-handyman.html": (
        "Oldsmar handyman for small jobs: drywall, doors, fixture plumbing, and punch lists. "
        "Registered and insured. Free written estimate."
    ),
    "tarpon-springs-handyman.html": (
        "Tarpon Springs handyman for fixture plumbing, drywall, doors, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "seminole-handyman.html": (
        "Seminole handyman for drywall, painting touch-ups, doors, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "northdale-handyman.html": (
        "Northdale handyman for drywall, painting, doors, and punch-list repairs in Hillsborough "
        "County. Registered and insured. Free written estimate."
    ),
    "egypt-lake-leto-handyman.html": (
        "Egypt Lake-Leto handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured Safety Harbor crew. Free written estimate."
    ),
    "town-n-country-handyman.html": (
        "Town 'n' Country handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "carrollwood-handyman.html": (
        "Carrollwood handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "westchase-handyman.html": (
        "Westchase handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "citrus-park-handyman.html": (
        "Citrus Park handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "beacon-square-handyman.html": (
        "Beacon Square handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "holiday-handyman.html": (
        "Holiday FL handyman for drywall, fixture plumbing, doors, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "elfers-handyman.html": (
        "Elfers handyman for drywall, doors, fixture plumbing, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "jasmine-estates-handyman.html": (
        "Jasmine Estates handyman for drywall, paint touch-ups, doors, and punch-list repairs. "
        "Registered and insured. Free written estimate."
    ),
    "seminole-interior-painting.html": (
        "Interior painting in Seminole FL: rooms, trim, stain blocking, and paint-ready drywall "
        "repair. Registered and insured. Free written estimate."
    ),
    "oldsmar-door-adjustment.html": (
        "Door adjustment in Oldsmar: sticking doors, hinges, latches, and alignment. Handyman-scope "
        "repair. Registered and insured. Free written estimate."
    ),
}

# Geo pages: also clean obvious keyword-stuffed hero leads.
HERO_OVERRIDES: dict[str, str] = {
    "temple-terrace-handyman.html": (
        "Temple Terrace handyman services — registered, insured Safety Harbor crew serving "
        "Hillsborough County river neighborhoods."
    ),
    "hillsborough-handyman.html": (
        "Hillsborough County handyman services — registered, insured Safety Harbor crew serving "
        "Tampa Bay neighborhoods."
    ),
    "pinellas-handyman.html": (
        "Pinellas County handyman services — registered, insured Safety Harbor crew for "
        "repairs, fixtures, drywall, and punch lists."
    ),
    "tampa-handyman.html": (
        "Tampa handyman services — registered, insured Safety Harbor crew serving "
        "Hillsborough County routes."
    ),
    "northdale-handyman.html": (
        "Northdale handyman services — registered, insured Safety Harbor crew serving "
        "Northdale Golf Club neighborhoods."
    ),
    "largo-handyman.html": (
        "Largo handyman services — registered, insured Safety Harbor crew serving Bardmoor "
        "and central Pinellas."
    ),
    "clearwater-handyman.html": (
        "Clearwater handyman services — registered, insured Safety Harbor crew serving "
        "Island Estates and inland Clearwater."
    ),
    "dunedin-handyman.html": (
        "Dunedin handyman services — registered, insured Safety Harbor crew serving "
        "downtown Dunedin."
    ),
}

TITLE_RE = re.compile(r"(<title>)([^<]*)(</title>)", re.I)
DESC_RE = re.compile(r'(<meta name="description" content=")([^"]*)(")', re.I)
OG_DESC_RE = re.compile(r'(<meta property="og:description" content=")([^"]*)(")', re.I)
TW_DESC_RE = re.compile(r'(<meta name="twitter:description" content=")([^"]*)(")', re.I)
OG_TITLE_RE = re.compile(r'(<meta property="og:title" content=")([^"]*)(")', re.I)
TW_TITLE_RE = re.compile(r'(<meta name="twitter:title" content=")([^"]*)(")', re.I)
HERO_RE = re.compile(
    r'(<p class="kg-page-hero__lead">)(.*?)(</p>)',
    re.I | re.S,
)


def esc(value: str) -> str:
    return html.escape(value.strip(), quote=True)


def replace_attr(pattern: re.Pattern[str], text: str, value: str) -> str:
    safe = esc(value)

    def repl(match: re.Match[str]) -> str:
        return match.group(1) + safe + match.group(3)

    if pattern.search(text):
        return pattern.sub(repl, text, count=1)
    return text


def replace_json_ld_descriptions(text: str, old: str, new: str) -> str:
    """Replace exact old description strings inside JSON-LD blocks."""
    if not old or old == new:
        return text
    variants = {old, html.unescape(old), esc(old)}
    for variant in variants:
        if not variant:
            continue
        text = text.replace(f'"description": "{variant}"', f'"description": "{esc(new)}"')
        text = text.replace(f'"description": "{html.escape(variant)}"', f'"description": "{esc(new)}"')
    return text


def update_meta_json() -> int:
    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    by_path = {str(e.get("path")): e for e in data.get("pages", [])}
    updated = 0
    for path, description in META_OVERRIDES.items():
        clean = clip_meta(description)
        if path in by_path:
            if by_path[path].get("description") != clean:
                by_path[path]["description"] = clean
                note = by_path[path].get("serper_note") or ""
                if "[ctr-fix-20260729]" not in note:
                    by_path[path]["serper_note"] = (note + " [ctr-fix-20260729]").strip()
                updated += 1
        else:
            data.setdefault("pages", []).append(
                {
                    "path": path,
                    "gsc_queries": [],
                    "serper_note": "Added by ctr-fix-20260729",
                    "description": clean,
                }
            )
            updated += 1
    META_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return updated


def patch_html(rel: str, *, title: str | None, description: str | None, hero: str | None) -> bool:
    path = ROOT / rel
    if not path.is_file():
        print(f"missing: {rel}")
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    old_desc_match = DESC_RE.search(text)
    old_desc = html.unescape(old_desc_match.group(2)) if old_desc_match else ""

    if title:
        text = replace_attr(TITLE_RE, text, title)
        text = replace_attr(OG_TITLE_RE, text, title)
        text = replace_attr(TW_TITLE_RE, text, title)
    if description:
        clean = clip_meta(description)
        text = replace_attr(DESC_RE, text, clean)
        text = replace_attr(OG_DESC_RE, text, clean)
        text = replace_attr(TW_DESC_RE, text, clean)
        text = replace_json_ld_descriptions(text, old_desc, clean)
    if hero:
        text = replace_attr(HERO_RE, text, hero)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"patched: {rel}")
        return True
    print(f"unchanged: {rel}")
    return False


def strip_llms_from_sitemap_builder() -> None:
    build = ROOT / "scripts" / "build-sitemap.py"
    text = build.read_text(encoding="utf-8")
    updated = text.replace('    ("/llms.txt", "0.40", "monthly"),\n', "")
    if updated != text:
        build.write_text(updated, encoding="utf-8")
        print("removed llms.txt from build-sitemap.py")


def rebuild_sitemap() -> None:
    import subprocess

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build-sitemap.py")])


def fix_geo_serp_keywords() -> None:
    """Stop mapping Hillsborough/Pasco cities to Pinellas SERP queries."""
    path = ROOT / "scripts" / "geo_serp_keywords.py"
    text = path.read_text(encoding="utf-8")
    replacements = {
        '"tampa": "handyman near me small jobs",': '"tampa": "handyman tampa fl",',
        '"town-n-country": "handyman near me small jobs",': '"town-n-country": "handyman tampa fl",',
        '"westchase": "small home renovations pinellas county",': '"westchase": "handyman westchase fl",',
        '"citrus-park": "general home repairs pinellas",': '"citrus-park": "handyman citrus park fl",',
        '"carrollwood": "handyman near me small jobs",': '"carrollwood": "handyman carrollwood fl",',
        '"northdale": "handyman painting pinellas county",': '"northdale": "handyman northdale fl",',
        '"egypt-lake-leto": "emergency handyman pinellas county",': '"egypt-lake-leto": "landlord handyman tampa",',
        '"temple-terrace": "carpentry services near me",': '"temple-terrace": "handyman temple terrace fl",',
        '"holiday": "plumbing services in pinellas county",': '"holiday": "handyman holiday fl",',
        '"trinity": "handyman estimate pinellas county",': '"trinity": "handyman trinity fl",',
        '"new-port-richey": "plumbing repair clearwater fl",': '"new-port-richey": "handyman new port richey fl",',
        '"elfers": "handyman near me small jobs",': '"elfers": "handyman elfers fl",',
        '"seven-springs": "carpenter pinellas county",': '"seven-springs": "handyman seven springs fl",',
        '"jasmine-estates": "handyman painting pinellas county",': '"jasmine-estates": "handyman jasmine estates fl",',
        '"beacon-square": "general home repairs pinellas",': '"beacon-square": "handyman beacon square fl",',
        '"port-richey": "door repair pinellas county",': '"port-richey": "handyman port richey fl",',
        '"land-o-lakes": "handyman estimate pinellas county",': '"land-o-lakes": "handyman land o lakes fl",',
        '"hillsborough": "handyman near me small jobs",': '"hillsborough": "handyman hillsborough county",',
        '"pasco": "plumbing services in pinellas county",': '"pasco": "handyman pasco county fl",',
        # Pinellas cities — keep local intent but avoid awkward stuffing phrases as "primary"
        '"dunedin": "handyman company pinellas",': '"dunedin": "dunedin handyman",',
        '"palm-harbor": "handyman pinellas county",': '"palm-harbor": "palm harbor handyman",',
        '"largo": "handyman pinellas county fl",': '"largo": "handyman largo",',
        '"oldsmar": "handyman near me small jobs",': '"oldsmar": "oldsmar handyman",',
        '"tarpon-springs": "plumbing services in pinellas county",': '"tarpon-springs": "tarpon springs handyman",',
        '"seminole": "handyman painting pinellas county",': '"seminole": "seminole handyman",',
    }
    updated = text
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        print("updated geo_serp_keywords.py primary queries")
    else:
        print("geo_serp_keywords.py already updated or patterns missed")


def main() -> int:
    json_n = update_meta_json()
    print(f"meta-descriptions.json entries updated: {json_n}")

    changed = 0
    all_paths = sorted(set(TITLE_OVERRIDES) | set(META_OVERRIDES) | set(HERO_OVERRIDES))
    for rel in all_paths:
        if patch_html(
            rel,
            title=TITLE_OVERRIDES.get(rel),
            description=META_OVERRIDES.get(rel),
            hero=HERO_OVERRIDES.get(rel),
        ):
            changed += 1
    print(f"HTML pages patched: {changed}")

    fix_geo_serp_keywords()
    strip_llms_from_sitemap_builder()
    rebuild_sitemap()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
