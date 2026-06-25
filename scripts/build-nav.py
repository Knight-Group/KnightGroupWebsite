#!/usr/bin/env python3
"""Regenerate desktop + mobile mega-menu blocks in header.html from seo/nav-catalog.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "header.html"
CATALOG = ROOT / "seo" / "nav-catalog.json"
MARKER_START = "<!-- KG-NAV-BUILD:START -->"
MARKER_END = "<!-- KG-NAV-BUILD:END -->"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_services_mega(catalog: dict) -> str:
    mega = catalog["servicesMega"]
    rows: list[str] = []
    rows.append(
        f"""        <li class="fw-services-mega__item">
          <a href="{esc(mega["overviewHref"])}" class="fw-services-mega__overview" role="menuitem">{esc(mega["overviewLabel"])}</a>
        </li>"""
    )
    for cat in mega["categories"]:
        flyout_id = f"kg-mega-{cat['id']}"
        flyout_items = []
        for link in cat["links"]:
            emphasis = ' class="fw-services-mega__emphasis"' if link.get("emphasis") else ""
            flyout_items.append(
                f'              <li class="fw-services-mega__flyout-item"><a href="{esc(link["href"])}" role="menuitem"{emphasis}>{esc(link["label"])}</a></li>'
            )
        rows.append(
            f"""        <li class="fw-services-mega__item fw-services-mega__item--branch">
          <button type="button" class="fw-services-mega__trigger subnav-toggle" aria-expanded="false" aria-haspopup="true" aria-controls="{flyout_id}">
            <span class="fw-services-mega__label">{esc(cat["label"])}</span>
            <span class="fw-services-mega__chevron" aria-hidden="true"></span>
          </button>
          <ul class="fw-services-mega__flyout" id="{flyout_id}" role="menu">
{chr(10).join(flyout_items)}
          </ul>
        </li>"""
        )
    return f"""<li class="nav-dropdown-wrap kg-nav-mega-wrap">
  <button type="button" class="nav-dropdown-btn services-link" aria-expanded="false" aria-haspopup="true">Services</button>
  <div class="nav-dropdown-menu fw-services-mega" role="menu">
    <ul class="fw-services-mega__list">
{chr(10).join(rows)}
    </ul>
  </div>
</li>"""


def render_areas_mega(catalog: dict) -> str:
    mega = catalog["areasMega"]
    rows: list[str] = []
    rows.append(
        f"""        <li class="fw-services-mega__item">
          <a href="{esc(mega["overviewHref"])}" class="fw-services-mega__overview" role="menuitem">{esc(mega["overviewLabel"])}</a>
        </li>"""
    )
    for region in mega["regions"]:
        flyout_id = f"kg-areas-{region['id']}"
        flyout_items = [
            f'              <li class="fw-services-mega__flyout-item"><a href="{esc(region["overviewHref"])}" role="menuitem">{esc(region["overviewLabel"])}</a></li>'
        ]
        for city in region["cities"]:
            flyout_items.append(
                f'              <li class="fw-services-mega__flyout-item"><a href="{esc(city["href"])}" role="menuitem">{esc(city["label"])}</a></li>'
            )
        rows.append(
            f"""        <li class="fw-services-mega__item fw-services-mega__item--branch">
          <button type="button" class="fw-services-mega__trigger subnav-toggle" aria-expanded="false" aria-haspopup="true" aria-controls="{flyout_id}">
            <span class="fw-services-mega__label">{esc(region["label"])}</span>
            <span class="fw-services-mega__chevron" aria-hidden="true"></span>
          </button>
          <ul class="fw-services-mega__flyout" id="{flyout_id}" role="menu">
{chr(10).join(flyout_items)}
          </ul>
        </li>"""
        )
    return f"""<li class="nav-dropdown-wrap kg-nav-mega-wrap">
  <button type="button" class="nav-dropdown-btn areas-link" aria-expanded="false" aria-haspopup="true">Service Areas</button>
  <div class="nav-dropdown-menu fw-services-mega kg-areas-mega" role="menu">
    <ul class="fw-services-mega__list">
{chr(10).join(rows)}
    </ul>
  </div>
</li>"""


def render_mobile_branch(cat_id: str, label: str, links: list[dict]) -> str:
    submenu_id = f"mm-{cat_id}"
    link_rows = "\n".join(
        f'      <a href="{esc(link["href"])}"{" class=\"fw-mm-emphasis\"" if link.get("emphasis") else ""}>{esc(link["label"])}</a>'
        for link in links
    )
    return f"""    <li class="fw-mm-item fw-mm-item--branch">
      <button class="fw-mm-trigger mm-services-toggle" type="button" aria-expanded="false" aria-controls="{submenu_id}">
        {esc(label)} <span class="mm-chevron">&#9660;</span>
      </button>
      <div class="fw-mm-submenu mm-submenu" id="{submenu_id}" hidden>
{link_rows}
      </div>
    </li>"""


def render_mobile_services(catalog: dict) -> str:
    mega = catalog["servicesMega"]
    rows = [
        f'    <li class="fw-mm-item"><a href="{esc(mega["overviewHref"])}">{esc(mega["overviewLabel"])}</a></li>'
    ]
    for cat in mega["categories"]:
        rows.append(render_mobile_branch(f"svc-{cat['id']}", cat["label"], cat["links"]))
    return "\n".join(rows)


def render_mobile_areas(catalog: dict) -> str:
    mega = catalog["areasMega"]
    rows = [
        f'    <li class="fw-mm-item"><a href="{esc(mega["overviewHref"])}">{esc(mega["overviewLabel"])}</a></li>'
    ]
    for region in mega["regions"]:
        links = [{"label": region["overviewLabel"], "href": region["overviewHref"]}, *region["cities"]]
        rows.append(render_mobile_branch(f"area-{region['id']}", region["label"], links))
    return "\n".join(rows)


def build_desktop_nav(catalog: dict) -> str:
    services = render_services_mega(catalog)
    areas = render_areas_mega(catalog)
    return f"""<nav><ul>
<li><a href="/about">About</a></li>
{services}
{areas}
<li><a href="/booking">Book Estimate</a></li>
<li><a href="/pricing">Pricing</a></li>
<li><a href="/contact">Contact</a></li>
<li><a href="/galleries">Gallery</a></li>
</ul></nav>"""


def build_mobile_nav(catalog: dict) -> str:
    services = render_mobile_services(catalog)
    areas = render_mobile_areas(catalog)
    return f"""<ul class="mm-nav">
<li><a href="/about">About</a></li>
<li class="fw-mm-item fw-mm-item--branch">
  <button class="fw-mm-trigger mm-services-toggle" type="button" aria-expanded="false" aria-controls="mmServicesRoot">
    Services <span class="mm-chevron">&#9660;</span>
  </button>
  <div class="fw-mm-submenu mm-submenu" id="mmServicesRoot" hidden>
    <ul class="fw-mm-list">
{services}
    </ul>
  </div>
</li>
<li class="fw-mm-item fw-mm-item--branch">
  <button class="fw-mm-trigger mm-services-toggle" type="button" aria-expanded="false" aria-controls="mmAreasRoot">
    Service Areas <span class="mm-chevron">&#9660;</span>
  </button>
  <div class="fw-mm-submenu mm-submenu" id="mmAreasRoot" hidden>
    <ul class="fw-mm-list">
{areas}
    </ul>
  </div>
</li>
<li><a href="/booking">Book Estimate</a></li>
<li><a href="/pricing">Pricing</a></li>
<li><a href="/contact">Contact</a></li>
<li><a href="/galleries">Gallery</a></li>
</ul>"""


def patch_header(catalog: dict) -> None:
    text = HEADER.read_text(encoding="utf-8")
    desktop = build_desktop_nav(catalog)
    mobile = build_mobile_nav(catalog)

    text = re.sub(
        r"<div class=\"nav-section\">.*?</div><div class=\"header-actions\">",
        f'<div class="nav-section">{desktop}</div><div class="header-actions">',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"<ul class=\"mm-nav\">.*?</ul><div class=\"mm-cta\">",
        f"{mobile}<div class=\"mm-cta\">",
        text,
        count=1,
        flags=re.S,
    )

    if MARKER_START in text:
        block = f"{MARKER_START}\n{MARKER_END}"
        text = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            block,
            text,
            flags=re.S,
        )

    if "kg-nav-mega.js" not in text:
        text = text.replace(
            "</nav><script>",
            '</nav><script src="/JS/kg-nav-mega.js?v=20260622-seo-nav" defer></script><script>',
            1,
        )

    HEADER.write_text(text, encoding="utf-8")
    print(f"Updated {HEADER.relative_to(ROOT)}")


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    patch_header(catalog)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
