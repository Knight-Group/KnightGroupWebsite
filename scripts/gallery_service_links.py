"""Map service page slugs to related gallery project detail pages."""

from __future__ import annotations

SERVICE_GALLERY_LINKS: dict[str, list[tuple[str, str]]] = {
    "handyman": [
        ("/gallery/fence-repair-before-after", "wooden fence repair"),
        ("/gallery/door-lock-repair-before-after", "door lock repair"),
        ("/gallery/carpet-removal-before-after", "carpet removal"),
        ("/gallery/filter-change-before-after", "HVAC filter change"),
    ],
    "general-repairs": [
        ("/gallery/mold-wall-repair", "Mold wall repair project"),
        ("/gallery/floor-subfloor-repair", "Floor and subfloor repair"),
        ("/gallery/blinds-replacement-before-after", "Blinds replacement"),
        ("/gallery/fire-extinguisher-mount-before-after", "fire extinguisher mount"),
        ("/gallery/stair-tape-repair-before-after", "stair safety tape"),
        ("/gallery/smoke-alarm-battery-swap-before-after", "smoke alarm battery swap"),
    ],
    "plumbing-services": [
        ("/gallery/pipe-repair-before-after", "Pipe repair before and after"),
        ("/gallery/tub-drain-replacement", "Tub drain replacement"),
        ("/gallery/garbage-disposal-install", "Garbage disposal install"),
        ("/gallery/kitchen-sink-leak-before-after", "kitchen sink leak"),
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
    "doors-windows": [
        ("/gallery/curtain-rod-mount-before-after", "curtain rod mount"),
        ("/gallery/door-lock-repair-before-after", "door lock repair"),
        ("/gallery/door-wedge-before-after", "door wedge install"),
        ("/gallery/blind-repair-before-after", "window blind repair"),
    ],
    "carpentry-framing": [
        ("/gallery/fence-repair-before-after", "wooden fence repair"),
        ("/gallery/fence-is-falling-down-and-needs-to-be-pu-b17b3ec-before-after", "leaning fence reset in Port Richey"),
        ("/gallery/floor-subfloor-repair", "floor and subfloor repair"),
    ],
    "cabinet-repair": [
        ("/gallery/kitchen-sink-leak-before-after", "kitchen sink leak closeout"),
    ],
}


def gallery_links_html(slug: str) -> str:
    links = SERVICE_GALLERY_LINKS.get(slug)
    if not links:
        return ""
    parts = ", ".join(f'<a href="{href}">{label}</a>' for href, label in links)
    return f"\n<p>Project photos: {parts}.</p>"
