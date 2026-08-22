#!/usr/bin/env python3
"""Remove Schema.org City nodes named North Tampa. Keep Lutz and Tampa. Prose may still say North Tampa."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from business_facts import write_entity_json_files  # noqa: E402

CITY_BLOCK = re.compile(
    r",\s*\{\s*\"@type\"\s*:\s*\"City\"\s*,\s*\"name\"\s*:\s*\"North Tampa, FL\"\s*\}",
    flags=re.S,
)


def strip_text(text: str) -> str:
    return CITY_BLOCK.sub("", text)


def main() -> int:
    write_entity_json_files()
    changed = 0
    for path in list(ROOT.rglob("*.html")) + list((ROOT / "seo").glob("*.json")):
        if any(part in {".git", "node_modules", "__pycache__", "docs"} for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        updated = strip_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(path.relative_to(ROOT))
    leftover = []
    for path in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules", "__pycache__"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r'"@type"\s*:\s*"City"[^}]*"North Tampa', text, flags=re.S):
            leftover.append(str(path.relative_to(ROOT)))
    entity = json.loads((ROOT / "seo" / "knight-group-business-entity.json").read_text(encoding="utf-8"))
    names = [n.get("name") for n in entity.get("areaServed", []) if isinstance(n, dict)]
    if "North Tampa, FL" in names:
        leftover.append("seo/knight-group-business-entity.json")
    if leftover:
        print("LEFTOVER North Tampa City nodes:", leftover)
        return 1
    print(f"stripped {changed} files; Lutz/Tampa City nodes kept")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
