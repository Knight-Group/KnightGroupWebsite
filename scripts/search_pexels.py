#!/usr/bin/env python3
"""Search Pexels HTML for photo IDs matching a query."""

from __future__ import annotations

import re
import sys
import urllib.request


def search_pexels(query: str, limit: int = 8) -> list[int]:
    q = urllib.parse.quote(query)
    url = f"https://www.pexels.com/search/{q}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
    ids = []
    for match in re.finditer(r"/photos/(\d+)/", html):
        pid = int(match.group(1))
        if pid not in ids:
            ids.append(pid)
        if len(ids) >= limit:
            break
    return ids


if __name__ == "__main__":
    import urllib.parse

    queries = sys.argv[1:] or [
        "tampa florida skyline",
        "clearwater beach florida pier",
        "st petersburg florida pier",
        "dunedin florida causeway",
        "tarpon springs sponge docks florida",
        "safety harbor florida",
        "land o lakes florida",
        "town n country florida",
        "new port richey florida",
        "holiday florida gulf",
    ]
    for query in queries:
        try:
            ids = search_pexels(query)
            print(query, "->", ids[:5])
        except Exception as exc:
            print(query, "ERROR", exc)
