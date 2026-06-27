#!/usr/bin/env python3
"""Validate Knight Group JSON-LD coverage on local HTML files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "seo" / "page-manifest.json"

BASE_REQUIREMENTS = {
    "Organization",
    "HomeAndConstructionBusiness",
    "WebSite",
    "WebPage",
    "BreadcrumbList",
}

CORE_REQUIREMENTS: dict[str, set[str]] = {
    "index.html": BASE_REQUIREMENTS | {"ContactPoint", "Person"},
    "services.html": BASE_REQUIREMENTS | {"ItemList"},
    "pricing.html": BASE_REQUIREMENTS | {"OfferCatalog"},
    "booking.html": BASE_REQUIREMENTS | {"ContactPage", "ContactAction", "Service"},
    "contact.html": BASE_REQUIREMENTS | {"ContactPage", "ContactAction"},
    "about.html": BASE_REQUIREMENTS | {"Person", "AboutPage"},
    "galleries.html": BASE_REQUIREMENTS | {"ImageGallery", "ImageObject", "ItemList"},
    "service-areas.html": BASE_REQUIREMENTS | {"Service"},
}

GEO_REQUIREMENTS = BASE_REQUIREMENTS | {"Service", "ImageObject", "FAQPage"}
SERVICE_REQUIREMENTS = BASE_REQUIREMENTS | {"Service", "ImageObject", "FAQPage"}
NICHE_REQUIREMENTS = BASE_REQUIREMENTS | {"Service", "ImageObject"}
POLICY_REQUIREMENTS = BASE_REQUIREMENTS


def load_types(path: Path) -> tuple[set[str], list[str]]:
    html = path.read_text(encoding="utf-8")
    issues: list[str] = []
    types: set[str] = set()
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.S | re.I,
    )
    if not blocks:
        issues.append("missing JSON-LD block")
        return types, issues
    if len(blocks) > 1:
        issues.append(f"multiple JSON-LD blocks ({len(blocks)})")

    for index, block in enumerate(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON-LD block #{index + 1}: {exc}")
            continue
        if ".html" in block:
            issues.append("schema URL contains .html")
        nodes = data.get("@graph", [data])
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node in nodes:
            node_type = node.get("@type")
            if isinstance(node_type, list):
                types.update(node_type)
            elif node_type:
                types.add(node_type)
            if node_type in {"ContactPage", "AboutPage"}:
                types.add("WebPage")
            action = node.get("potentialAction")
            if isinstance(action, dict) and action.get("@type"):
                types.add(action["@type"])
            contact_point = node.get("contactPoint")
            if contact_point:
                if isinstance(contact_point, list):
                    for item in contact_point:
                        if isinstance(item, dict) and item.get("@type"):
                            types.add(item["@type"])
                elif isinstance(contact_point, dict) and contact_point.get("@type"):
                    types.add(contact_point["@type"])

    return types, issues


def requirements_for(rel_path: str) -> set[str]:
    if rel_path in CORE_REQUIREMENTS:
        return CORE_REQUIREMENTS[rel_path]
    if rel_path.startswith("PolicyPages/"):
        return POLICY_REQUIREMENTS
    if rel_path.startswith("Services/"):
        return SERVICE_REQUIREMENTS
    if rel_path.endswith("-handyman.html") or "-repair" in rel_path or "-adjustment" in rel_path or "-painting" in rel_path:
        return GEO_REQUIREMENTS
    if rel_path.startswith("pricing-"):
        return BASE_REQUIREMENTS | {"OfferCatalog"}
    if rel_path.startswith("gallery/"):
        return BASE_REQUIREMENTS | {"CreativeWork"}
    return BASE_REQUIREMENTS | {"Service"}


def collect_targets() -> list[tuple[str, set[str]]]:
    targets: list[tuple[str, set[str]]] = []
    for rel_path, required in CORE_REQUIREMENTS.items():
        targets.append((rel_path, required))
    for path in sorted((ROOT / "PolicyPages").glob("*.html")):
        targets.append((f"PolicyPages/{path.name}", POLICY_REQUIREMENTS))
    for path in sorted((ROOT / "Services").glob("*.html")):
        if path.name in {"index.html", "programming&databases.html", "handcraftedfurniture&resins.html"}:
            continue
        targets.append((f"Services/{path.name}", SERVICE_REQUIREMENTS))
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for entry in manifest.get("pages", []):
            rel_path = entry["path"]
            page_type = entry.get("pageType", "")
            if page_type in {"city", "county", "city-service"}:
                targets.append((rel_path, GEO_REQUIREMENTS))
            elif page_type == "niche-service":
                targets.append((rel_path, NICHE_REQUIREMENTS))
            elif page_type == "pricing-niche":
                targets.append((rel_path, BASE_REQUIREMENTS | {"OfferCatalog"}))
            elif page_type == "gallery-project":
                targets.append((rel_path, BASE_REQUIREMENTS | {"CreativeWork"}))
    return targets


def main() -> int:
    failures = 0
    report: list[dict[str, object]] = []
    seen: set[str] = set()

    for rel_path, required in collect_targets():
        if rel_path in seen:
            continue
        seen.add(rel_path)
        path = ROOT / rel_path
        if not path.exists():
            print(f"FAIL {rel_path}: file missing")
            failures += 1
            continue
        types, issues = load_types(path)
        missing = sorted(required - types)
        if issues or missing:
            failures += 1
            print(f"FAIL {rel_path}")
            for issue in issues:
                print(f"  - {issue}")
            if missing:
                print(f"  - missing types: {', '.join(missing)}")
            report.append(
                {
                    "page": rel_path,
                    "status": "fail",
                    "types": sorted(types),
                    "issues": issues + ([f"missing types: {', '.join(missing)}"] if missing else []),
                }
            )
        else:
            print(f"OK   {rel_path}")
            report.append({"page": rel_path, "status": "ok", "types": sorted(types), "issues": []})

    report_path = ROOT / "seo" / "schema-verification-report.json"
    report_path.write_text(
        json.dumps({"pages": report, "failed": failures, "checked": len(seen)}, indent=2),
        encoding="utf-8",
    )
    print(f"\nChecked {len(seen)} pages. Failures: {failures}")
    print(f"Report written to {report_path.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
