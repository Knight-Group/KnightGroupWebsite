#!/usr/bin/env python3
"""Validate a tracked static site without network access or source mutations."""
from __future__ import annotations

import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".txt", ".xml", ".webmanifest"}
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
IMAGE_BUDGET = 3_000_000
SKIP_CANONICAL = {"404.html", "thank-you.html"}
NONPUBLIC_DIRS = {".github", "admin", "docs", "node_modules", "scripts"}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        ROOT / item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []
        self.refs: list[str] = []
        self.schemas: list[str] = []
        self._schema_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "link" and "canonical" in (values.get("rel") or "").lower().split():
            if values.get("href"):
                self.canonicals.append(values["href"])
        for key in ("href", "src"):
            if values.get(key):
                self.refs.append(values[key])
        if values.get("srcset"):
            self.refs.extend(
                part.strip().split()[0]
                for part in values["srcset"].split(",")
                if part.strip()
            )
        if tag == "script" and (values.get("type") or "").lower() == "application/ld+json":
            self._schema_parts = []

    def handle_data(self, data: str) -> None:
        if self._schema_parts is not None:
            self._schema_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._schema_parts is not None:
            self.schemas.append("".join(self._schema_parts).strip())
            self._schema_parts = None


def normalized_host(value: str) -> str:
    return value.lower().removeprefix("www.")


def local_target(page: Path, ref: str) -> Path | None:
    ref = ref.strip()
    if not ref or ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return None
    if any(token in ref for token in ("{{", "}}", "<%", "%>")):
        return None
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    target = ROOT / clean.lstrip("/") if clean.startswith("/") else page.parent / clean
    target = target.resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return target
    if clean.endswith("/"):
        return target / "index.html"
    if not target.suffix:
        html_target = target.with_suffix(".html")
        if html_target.exists():
            return html_target
        return target / "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    tracked = tracked_files()
    domain = (ROOT / "CNAME").read_text(encoding="utf-8").strip()

    sitemap = ROOT / "sitemap.xml"
    locations: list[str] = []
    public_html = {ROOT / "index.html"}
    if not sitemap.exists():
        errors.append("sitemap.xml: missing")
    else:
        try:
            tree = ElementTree.parse(sitemap)
            locations = [
                (node.text or "").strip()
                for node in tree.iter()
                if node.tag.rsplit("}", 1)[-1] == "loc"
            ]
        except ElementTree.ParseError as exc:
            errors.append(f"sitemap.xml: invalid XML ({exc})")
        for location in locations:
            parsed = urlparse(location)
            if normalized_host(parsed.hostname or "") != normalized_host(domain):
                errors.append(f"sitemap.xml: domain mismatch {location}")
                continue
            route = unquote(parsed.path).lstrip("/")
            target = ROOT / ("index.html" if not route else route)
            if route.endswith("/"):
                target = target / "index.html"
            elif not target.suffix:
                target = target.with_suffix(".html")
            if not target.exists():
                errors.append(f"sitemap.xml: missing page for {location}")
            elif target.suffix.lower() == ".html":
                public_html.add(target)

    for path in tracked:
        relative_parts = {part.lower() for part in path.relative_to(ROOT).parts[:-1]}
        if path.suffix.lower() in TEXT_SUFFIXES and not relative_parts.intersection(NONPUBLIC_DIRS):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"{path.relative_to(ROOT)}: invalid UTF-8 ({exc})")
                continue
            for marker in ("\ufffd", "â€", "Â·", "Ã©", "Ã¢"):
                if marker in text:
                    errors.append(f"{path.relative_to(ROOT)}: mojibake marker {marker!r}")

    html_files = sorted(path for path in public_html if path.exists())
    referenced_images: set[Path] = set()
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        rel = page.relative_to(ROOT)
        is_document = "<html" in text.lower()
        if is_document and page.name not in SKIP_CANONICAL:
            if len(parser.canonicals) != 1:
                errors.append(f"{rel}: expected one canonical, found {len(parser.canonicals)}")
            else:
                canonical = urlparse(parser.canonicals[0])
                if canonical.scheme != "https" or normalized_host(canonical.hostname or "") != normalized_host(domain):
                    errors.append(f"{rel}: canonical does not match CNAME {domain}")
        for index, schema in enumerate(parser.schemas, start=1):
            try:
                json.loads(schema)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD block {index} ({exc})")
        for ref in parser.refs:
            target = local_target(page, ref)
            if target is not None and not target.exists():
                errors.append(f"{rel}: missing local reference {ref}")
            elif target is not None and target.suffix.lower() in IMAGE_SUFFIXES:
                referenced_images.add(target)

    for image in sorted(referenced_images):
        if image.stat().st_size > IMAGE_BUDGET:
            errors.append(
                f"{image.relative_to(ROOT)}: {image.stat().st_size} bytes exceeds {IMAGE_BUDGET}"
            )

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        print(f"Static-site validation failed with {len(errors)} error(s).")
        return 1
    print(
        f"Validated {len(html_files)} HTML files, sitemap, canonicals, JSON-LD, "
        "internal references, UTF-8 encoding, and image budgets."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
