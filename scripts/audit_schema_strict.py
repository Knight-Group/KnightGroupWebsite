#!/usr/bin/env python3
"""Stricter JSON-LD checks aligned with common crawler validators."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"scripts", "legacy", "admin", "node_modules", ".venv", "seo", "Chess-Game-main", "page-template.html"}


def walk_nodes(data: object, nodes: list[dict]) -> None:
    if isinstance(data, dict):
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                walk_nodes(item, nodes)
            return
        nodes.append(data)
        for value in data.values():
            walk_nodes(value, nodes)
    elif isinstance(data, list):
        for item in data:
            walk_nodes(item, nodes)


def main() -> int:
    failures = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        html = path.read_text(encoding="utf-8", errors="ignore")
        blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, flags=re.S | re.I)
        page_issues: list[str] = []
        for index, block in enumerate(blocks):
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                page_issues.append(f"invalid JSON block {index + 1}: {exc}")
                continue
            if ".html" in block:
                page_issues.append("schema contains .html in URL")
            nodes: list[dict] = []
            walk_nodes(data, nodes)
            ids_seen: dict[str, int] = {}
            for node in nodes:
                node_id = node.get("@id")
                if isinstance(node_id, str):
                    ids_seen[node_id] = ids_seen.get(node_id, 0) + 1
                node_type = node.get("@type")
                if node_type == "FAQPage":
                    entities = node.get("mainEntity")
                    if not entities:
                        page_issues.append("FAQPage missing mainEntity")
                if node_type == "Service":
                    if not node.get("name"):
                        page_issues.append("Service missing name")
                    image = node.get("image")
                    if not image:
                        page_issues.append("Service missing image")
                if node_type == "ImageObject" and not node.get("url") and not node.get("contentUrl"):
                    page_issues.append("ImageObject missing url/contentUrl")
            dupes = [node_id for node_id, count in ids_seen.items() if count > 1]
            if dupes:
                page_issues.append(f"duplicate @id values: {', '.join(dupes[:3])}")
        if page_issues:
            failures += 1
            print(f"SCHEMA {rel}")
            for issue in page_issues:
                print(f"  - {issue}")
    if not failures:
        print("Strict schema audit passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
