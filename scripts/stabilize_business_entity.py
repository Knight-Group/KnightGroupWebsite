#!/usr/bin/env python3
"""Make #business identical on every public page. Home Watch #service stays Pinellas-only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from business_facts import BUSINESS_DESCRIPTION  # noqa: E402
from schema_graph import business_entity  # noqa: E402

OLD_DESCRIPTION = (
    "Knight Group Handyman Services LLC provides registered and insured handyman services "
    "and recurring Home Watch / vacant-property checks across Safety Harbor and Pinellas County, Florida."
)
BUSINESS_ID = "https://www.knightgroup.com/#business"
LD_RE = re.compile(
    r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)',
    flags=re.S | re.I,
)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "scripts", "docs"}


def _area_names(served: object) -> tuple[str, ...]:
    if isinstance(served, dict):
        name = served.get("name")
        return (str(name),) if name else ()
    if not isinstance(served, list):
        return ()
    names: list[str] = []
    for item in served:
        if isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
        elif item:
            names.append(str(item))
    return tuple(sorted(names))


def _needs_area_rewrite(node: dict, canonical: dict) -> bool:
    return _area_names(node.get("areaServed")) != _area_names(canonical.get("areaServed"))


def _fix_graph(data: object, canonical: dict) -> bool:
    changed = False
    nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
    if not isinstance(nodes, list):
        nodes = [nodes]
    for node in nodes:
        if not isinstance(node, dict) or node.get("@id") != BUSINESS_ID:
            continue
        if node.get("description") != canonical["description"]:
            node["description"] = canonical["description"]
            changed = True
        if _needs_area_rewrite(node, canonical):
            node["areaServed"] = canonical["areaServed"]
            changed = True
    return changed


def main() -> int:
    canonical = business_entity()
    if canonical.get("description") != BUSINESS_DESCRIPTION:
        print("canonical description mismatch")
        return 1
    text_hits = 0
    json_hits = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = original.replace(OLD_DESCRIPTION, BUSINESS_DESCRIPTION)
        if updated != original:
            text_hits += 1

        def replacer(match: re.Match[str]) -> str:
            nonlocal json_hits
            raw = match.group(2)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return match.group(0)
            nodes = data.get("@graph", [data]) if isinstance(data, dict) else [data]
            needs_area = any(
                isinstance(node, dict)
                and node.get("@id") == BUSINESS_ID
                and _needs_area_rewrite(node, canonical)
                for node in nodes
            )
            if not _fix_graph(data, canonical) or not needs_area:
                return match.group(0)
            json_hits += 1
            pretty = json.dumps(data, indent=4, ensure_ascii=False)
            return f"{match.group(1)}{pretty}{match.group(3)}"

        rewritten = LD_RE.sub(replacer, updated)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            print(path.relative_to(ROOT))
    print(f"description string replacements: {text_hits}; JSON-LD #business areaServed rewrites: {json_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
