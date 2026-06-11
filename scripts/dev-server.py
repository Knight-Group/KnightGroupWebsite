#!/usr/bin/env python3
"""Local static server with production-style clean URLs for Knight Group."""

from __future__ import annotations

import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8082


class KnightGroupDevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        resolved = self._resolve_clean_url(self.path)
        if resolved:
            self.path = resolved
        return super().do_GET()

    def _resolve_clean_url(self, raw_path: str) -> str | None:
        path_only = unquote(raw_path.split("?", 1)[0].split("#", 1)[0])
        if not path_only or path_only == "/":
            index_path = ROOT / "index.html"
            if index_path.is_file():
                return "/index.html"
            return None

        relative = path_only.lstrip("/").rstrip("/")
        if not relative:
            return "/index.html"

        # Hub page: /services and /Services must not open the Services/ directory on Windows.
        if relative.lower() == "services":
            hub = ROOT / "services.html"
            if hub.is_file():
                return "/services.html"

        html_candidate = ROOT / f"{relative}.html"
        if html_candidate.is_file():
            return "/" + html_candidate.relative_to(ROOT).as_posix()

        candidate = ROOT / relative
        if candidate.is_file():
            return None

        if candidate.is_dir():
            index_file = candidate / "index.html"
            if index_file.is_file():
                return "/" + index_file.relative_to(ROOT).as_posix()

        return None

    def log_message(self, format: str, *args) -> None:
        sys.stdout.write("[%s] %s - %s\n" % (self.log_date_time_string(), self.address_string(), format % args))


def main() -> int:
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = ThreadingHTTPServer(("127.0.0.1", port), KnightGroupDevHandler)
    print(f"Serving Knight Group at http://127.0.0.1:{port}/")
    print("Clean URLs enabled (e.g. /about -> about.html)")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
