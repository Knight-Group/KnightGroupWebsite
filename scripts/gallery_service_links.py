"""Map service page slugs to related gallery project detail pages."""

from __future__ import annotations

SERVICE_GALLERY_LINKS: dict[str, list[tuple[str, str]]] = {
    "general-repairs": [
        ("/gallery/mold-wall-repair", "Mold wall repair project"),
        ("/gallery/floor-subfloor-repair", "Floor and subfloor repair"),
        ("/gallery/blinds-replacement-before-after", "Blinds replacement"),
    ],
    "plumbing-services": [
        ("/gallery/pipe-repair-before-after", "Pipe repair before and after"),
        ("/gallery/tub-drain-replacement", "Tub drain replacement"),
        ("/gallery/garbage-disposal-install", "Garbage disposal install"),
    ],
    "home-renovations": [
        ("/gallery/bathroom-remodel-cobblestone", "Bathroom remodel with cobblestone flooring"),
        ("/gallery/bathroom-tub-window-remodel", "Bathroom tub and window remodel"),
    ],
    "garbage-disposal-replacement": [
        ("/gallery/garbage-disposal-install", "Garbage disposal installation project"),
    ],
    "drywall-repair": [
        ("/gallery/mold-wall-repair", "Mold-affected wall repair"),
    ],
    "painting-finishing": [
        ("/gallery/blinds-replacement-before-after", "Blinds replacement project"),
    ],
}


def gallery_links_html(slug: str) -> str:
    links = SERVICE_GALLERY_LINKS.get(slug)
    if not links:
        return ""
    parts = ", ".join(f'<a href="{href}">{label}</a>' for href, label in links)
    return f"\n<p>Project photos: {parts}.</p>"
