#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for name in ["Services/handyman.html", "tampa-handyman.html", "hillsborough-handyman.html", "index.html"]:
    html = (root / name).read_text(encoding="utf-8")
    m = re.search(r"ld\+json\">\s*(\{.*?\})\s*</script>", html, re.S)
    data = json.loads(m.group(1))
    types = sorted({n.get("@type") for n in data["@graph"] if n.get("@type")})
    print(name, "nodes", len(data["@graph"]), "types", types)
print("sitemap urls", (root / "sitemap.xml").read_text(encoding="utf-8").count("<loc>"))
print("serp queries", json.loads((root / "seo/serp-meta-research.json").read_text())["query_count"])
