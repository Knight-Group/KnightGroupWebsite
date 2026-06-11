#!/usr/bin/env python3
"""Validate Knight Group JSON-LD coverage on local HTML files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIREMENTS: dict[str, set[str]] = {
    "index.html": {"Organization", "HomeAndConstructionBusiness", "WebSite", "WebPage", "BreadcrumbList"},
    "services.html": {
        "Organization",
        "HomeAndConstructionBusiness",
        "WebSite",
        "WebPage",
        "BreadcrumbList",
        "ItemList",
        "FAQPage",
    },
    "pricing.html": {"Organization", "OfferCatalog", "BreadcrumbList", "WebPage"},
    "booking.html": {"Organization", "ContactPage", "ContactAction", "BreadcrumbList"},
    "contact.html": {"Organization", "ContactPage", "BreadcrumbList"},
    "about.html": {"Organization", "Person", "AboutPage", "BreadcrumbList"},
    "galleries.html": {"Organization", "ImageGallery", "ImageObject", "BreadcrumbList"},
    "service-areas.html": {"Organization", "Service", "BreadcrumbList", "WebPage"},
    "pinellas-handyman.html": {"Organization", "HomeAndConstructionBusiness", "Service", "BreadcrumbList"},
    "clearwater-handyman.html": {"Organization", "HomeAndConstructionBusiness", "Service", "BreadcrumbList"},
}

SERVICE_REQUIREMENTS = {
    "Organization",
    "HomeAndConstructionBusiness",
    "WebSite",
    "WebPage",
    "Service",
    "BreadcrumbList",
    "FAQPage",
}


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
            action = node.get("potentialAction")
            if isinstance(action, dict) and action.get("@type"):
                types.add(action["@type"])

    return types, issues


def main() -> int:
    failures = 0
    report: list[dict[str, object]] = []
    targets = list(REQUIREMENTS.items())
    for path in sorted((ROOT / "Services").glob("*.html")):
        if path.name in {"index.html", "programming&databases.html", "handcraftedfurniture&resins.html"}:
            continue
        targets.append((f"Services/{path.name}", SERVICE_REQUIREMENTS))

    for rel_path, required in targets:
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
        json.dumps({"pages": report, "failed": failures}, indent=2),
        encoding="utf-8",
    )
    print(f"\nReport written to {report_path.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
