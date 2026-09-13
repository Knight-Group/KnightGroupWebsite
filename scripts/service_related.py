"""Related-service card links and trade image resolution for service/geo pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from seo_page_data import NICHE_SERVICES, PARENT_LABELS

ROOT = Path(__file__).resolve().parents[1]
SERVICES_IMG_DIR = ROOT / "Images" / "services"
CITIES_IMG_DIR = ROOT / "Images" / "cities"
GALLERY_DIR = ROOT / "GalleryImages"
GALLERY_MANIFEST = GALLERY_DIR / "gallery-manifest.json"
FACE_CARD_TOKENS = ("about-vince-face", "kghero_person_crop")

_GALLERY_COVERS: dict[str, str] | None = None


def _job(name: str) -> str:
    """Public gallery still or named job photo. Prefer these over stock trade cards."""
    return f"/GalleryImages/{name}"


# Parent trade pages — last-resort stock files if a job still is missing.
SERVICE_CARD_IMAGES: dict[str, str] = {
    "handyman": "handyman.webp",
    "general-repairs": "general-repairs.webp",
    "plumbing-services": "plumbing-services.webp",
    "electrical-work": "electrical-work.webp",
    "carpentry-framing": "carpentry-framing.webp",
    "painting-finishing": "painting-finishing.webp",
    "home-renovations": "home-renovations.webp",
    "doors-windows": "doors-windows.webp",
    "custom-projects": "custom-projects.webp",
    "emergency-services": "emergency-services.webp",
}

NICHE_PARENT: dict[str, str] = {item["slug"]: item["parent"] for item in NICHE_SERVICES}

# Default related trades shown on city/county geo pages (services only).
CORE_GEO_RELATED: list[tuple[str, str]] = [
    ("/Services/handyman", "Handyman services"),
    ("/Services/general-repairs", "General repairs"),
    ("/Services/plumbing-services", "Plumbing services"),
    ("/Services/doors-windows", "Doors & windows"),
]

# Fourth related service on combo pages when parent is already in the list above.
PARENT_NICHE_EXTRAS: dict[str, tuple[str, str]] = {
    "plumbing-services": ("/Services/faucet-replacement", "Faucet replacement planning"),
    "general-repairs": ("/Services/drywall-repair", "Drywall repair"),
    "handyman": ("/Services/small-jobs", "Small jobs"),
    "carpentry-framing": ("/Services/trim-repair", "Trim repair"),
    "painting-finishing": ("/Services/interior-painting", "Interior painting"),
    "doors-windows": ("/Services/door-adjustment", "Door adjustment"),
    "electrical-work": ("/Services/electrical-work", "Electrical work"),
    "home-renovations": ("/Services/custom-projects", "Custom projects"),
    "emergency-services": ("/Services/emergency-services", "Emergency services"),
    "custom-projects": ("/Services/carpentry-framing", "Carpentry & framing"),
}

SAFE_RELATED_LABELS: dict[str, str] = {}


def unescape_related_label(label: str) -> str:
    prev = label or ""
    for _ in range(8):
        nxt = html.unescape(prev)
        if nxt == prev:
            break
        prev = nxt
    return prev


def safe_related_label(href: str, label: str) -> str:
    """Pass through card labels. Fixture and fan work are in-scope."""
    path = href.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    return SAFE_RELATED_LABELS.get(path, unescape_related_label(label))


def related_slug(href: str) -> str:
    return href.rstrip("/").split("/")[-1].replace(".html", "")


# Non-service destinations. Job photos, never the same file twice on one grid.
PAGE_CARD_IMAGES: dict[str, str] = {
    "/galleries": _job("after-laminate-lvp-installation-d86a9bf.webp"),
    "/booking": "/Images/Knight-Hammer.webp",
    "/about": "/Images/related/about-vince-face.webp",
    "/pricing": _job("after-transition-strip-98fcc0e.webp"),
    "/pricing-no-2-hour-minimum": _job("after-change-lock-set-on-2-with-4-matching-key-03d49fa.webp"),
    "/pricing-handyman-by-the-hour": _job("after-handyman-repair-669cf03.webp"),
    "/pricing-flat-rate-handyman": _job("after-fence-and-garage-5544008.webp"),
    "/pricing-plumbing-repair-prices": _job("after-2-toilets-7f8c499.webp"),
    "/service-areas": "/Images/cities/safety-harbor.webp",
    "/contact": _job("after-fence-is-falling-down-and-needs-to-be-pu-b17b3ec.webp"),
    "/services": _job("after-repair-kithchen-cabinets-9e04de2.webp"),
    "/home-watch-pinellas": _job("after-clean-exterior-front-of-house-70a4580.webp"),
    "/home-watch-pricing": _job("after-pressure-wash-walk-way-b49a8fd.webp"),
    "/home-watch-checklist": _job("after-wasp-bee-nest-removal-request-0f9dd4b.webp"),
    "/home-watch-sample-report": _job("after-clean-exterior-front-of-house-70a4580.webp"),
    "/florida-snowbird-departure-checklist": _job("after-side-yard-gate-repair-18bb381.webp"),
    "/rental-turnover-handyman": _job("Refinished_Bathroom.webp"),
    "/property-manager-handyman": _job("Refinished_Room2.webp"),
    "/hurricane-repair-handyman-pinellas": _job("after-front-fence-repair-08fc100.webp"),
    "/plumber-background-handyman": _job("after-cabinet-repair-339b0d9.webp"),
    "/handyman-scope-florida": _job("after-handyman-repair-669cf03.webp"),
}

# Service / niche slugs. Each destination gets its own Knight Group job still.
SLUG_CARD_IMAGES: dict[str, str] = {
    "handyman": _job("after-transition-strip-98fcc0e.webp"),
    "home-repair-near-me": _job("Refinished_Room2.webp"),
    "small-jobs": _job("after-change-lock-set-on-2-with-4-matching-key-03d49fa.webp"),
    "general-repairs": _job("after-attic-drywall-return-visit-54b0dce.webp"),
    "drywall-repair": _job("after-ceiling-drywall-patch-2f1127e.webp"),
    "drywall-paint-repair": _job("Refinished_Room2.webp"),
    "water-damage-repair": _job("after-repair-ceiling-in-bathroom-f739128.webp"),
    "hole-in-wall-repair": _job("after-rodent-hole-sealing-a-b-1c2096d.webp"),
    "caulking-repair": _job("after-sink-drain-caulk-trap-leak-7843b10.webp"),
    "mobile-home-repairs": _job("after-laminate-lvp-installation-d86a9bf.webp"),
    "plumbing-services": _job("after-facuet-replacement-d864caa.webp"),
    "plumber-background-handyman": _job("after-cabinet-repair-339b0d9.webp"),
    "sink-faucet-repair": _job("after-kitchen-sink-drain-service-c8d521c.webp"),
    "faucet-replacement": _job("after-recaulk-around-kitchen-windowsill-custom-5cca131.webp"),
    "toilet-repair": _job("after-toilet-0ff372e.webp"),
    "garbage-disposal-replacement": _job("GarbageDisposal.webp"),
    "shutoff-valve-repair": _job("after-inspect-water-leaks-08cb97a.webp"),
    "drain-unclogging": _job("after-sink-drain-pop-up-assembly-36b860c.webp"),
    "electrical-work": _job("after-ceiling-fan-repair-1e73090.webp"),
    "carpentry-framing": _job("after-repair-kithchen-cabinets-9e04de2.webp"),
    "small-job-carpenter": _job("after-corner-cabinet-shelf-repair-bc5b1e2.webp"),
    "trim-repair": _job("after-laminate-lvp-installation-d86a9bf.webp"),
    "custom-shelving": _job("after-corner-cabinet-shelf-repair-bc5b1e2.webp"),
    "cabinet-repair": _job("after-repair-kithchen-cabinets-9e04de2.webp"),
    "door-frame-repair": _job("after-bedroom-d9d0055.webp"),
    "painting-finishing": _job("Refinished_Bathroom.webp"),
    "interior-painting": _job("Refinished_Room2.webp"),
    "texture-matching": _job("after-attic-drywall-return-visit-54b0dce.webp"),
    "trim-painting": _job("after-bedroom-d9d0055.webp"),
    "home-renovations": _job("after-laminate-lvp-installation-d86a9bf.webp"),
    "doors-windows": _job("after-bedroom-d9d0055.webp"),
    "sliding-door-repair": _job("after-threshold-9826926.webp"),
    "screen-door-repair": _job("after-exterior-coping-and-screens-f1920f7.webp"),
    "window-screen-repair": _job("after-recaulk-around-kitchen-windowsill-custom-5cca131.webp"),
    "door-adjustment": _job("after-threshold-9826926.webp"),
    "custom-projects": _job("after-corner-cabinet-shelf-repair-bc5b1e2.webp"),
    "emergency-services": _job("after-wasp-bee-nest-removal-request-0f9dd4b.webp"),
    "hurricane-repair-handyman-pinellas": _job("after-front-fence-repair-08fc100.webp"),
    "rental-turnover-handyman": _job("Refinished_Bathroom.webp"),
    "property-manager-handyman": _job("Refinished_Room2.webp"),
    "handyman-scope-florida": _job("after-handyman-repair-669cf03.webp"),
}

# Same-topic stills used only when two cards would otherwise share a file.
TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "plumbing": (
        "plumb",
        "faucet",
        "facuet",
        "toilet",
        "disposal",
        "drain",
        "sink",
        "shutoff",
        "valve",
        "pipe",
        "tub",
        "shower",
        "leak",
    ),
    "electrical": ("electrical", "fan", "outlet", "fixture", "ballast", "smoke"),
    "drywall": ("drywall", "texture", "hole-in-wall", "water-damage", "ceiling"),
    "paint": ("paint", "refinish"),
    "carpentry": ("carpent", "cabinet", "shelf", "trim", "laminate", "floor", "subfloor"),
    "doors": ("door", "window", "screen", "lock", "threshold", "blinds"),
    "exterior": (
        "fence",
        "hurricane",
        "storm",
        "wasp",
        "pressure",
        "exterior",
        "gate",
        "home-watch",
        "snowbird",
        "watch",
    ),
    "about": ("about",),
    "booking": ("booking", "estimate"),
}

TOPIC_POOLS: dict[str, tuple[str, ...]] = {
    "plumbing": (
        _job("after-facuet-replacement-d864caa.webp"),
        _job("after-cabinet-repair-339b0d9.webp"),
        _job("GarbageDisposal.webp"),
        _job("after-toilet-0ff372e.webp"),
        _job("after-2-toilets-7f8c499.webp"),
        _job("after-inspect-water-leaks-08cb97a.webp"),
        _job("after-sink-drain-pop-up-assembly-36b860c.webp"),
        _job("after-kitchen-sink-drain-service-c8d521c.webp"),
    ),
    "electrical": (
        _job("after-ceiling-fan-repair-1e73090.webp"),
        _job("after-ballast-light-fixture-bbe38e2.webp"),
        _job("after-a-wall-outlet-repair-93788a6.webp"),
    ),
    "drywall": (
        _job("after-ceiling-drywall-patch-2f1127e.webp"),
        _job("after-attic-drywall-return-visit-54b0dce.webp"),
        _job("after-repair-ceiling-in-bathroom-f739128.webp"),
        _job("after-rodent-hole-sealing-a-b-1c2096d.webp"),
    ),
    "paint": (
        _job("Refinished_Room2.webp"),
        _job("Refinished_Bathroom.webp"),
        _job("after-repair-ceiling-in-bathroom-f739128.webp"),
    ),
    "carpentry": (
        _job("after-repair-kithchen-cabinets-9e04de2.webp"),
        _job("after-corner-cabinet-shelf-repair-bc5b1e2.webp"),
        _job("after-laminate-lvp-installation-d86a9bf.webp"),
        _job("after-transition-strip-98fcc0e.webp"),
    ),
    "doors": (
        _job("after-bedroom-d9d0055.webp"),
        _job("after-change-lock-set-on-2-with-4-matching-key-03d49fa.webp"),
        _job("after-threshold-9826926.webp"),
        _job("after-exterior-coping-and-screens-f1920f7.webp"),
        _job("after-handyman-repair-669cf03.webp"),
    ),
    "exterior": (
        _job("after-front-fence-repair-08fc100.webp"),
        _job("after-side-yard-gate-repair-18bb381.webp"),
        _job("after-clean-exterior-front-of-house-70a4580.webp"),
        _job("after-wasp-bee-nest-removal-request-0f9dd4b.webp"),
        _job("after-pressure-wash-walk-way-b49a8fd.webp"),
        _job("after-exterior-coping-and-screens-f1920f7.webp"),
    ),
    "about": ("/Images/related/about-vince-face.webp",),
    "booking": ("/Images/Knight-Hammer.webp",),
}

UNIQUE_FALLBACKS: tuple[str, ...] = (
    _job("after-facuet-replacement-d864caa.webp"),
    _job("after-cabinet-repair-339b0d9.webp"),
    _job("GarbageDisposal.webp"),
    _job("after-toilet-0ff372e.webp"),
    _job("after-ceiling-fan-repair-1e73090.webp"),
    _job("after-attic-drywall-return-visit-54b0dce.webp"),
    _job("after-ceiling-drywall-patch-2f1127e.webp"),
    _job("after-repair-kithchen-cabinets-9e04de2.webp"),
    _job("after-corner-cabinet-shelf-repair-bc5b1e2.webp"),
    _job("after-bedroom-d9d0055.webp"),
    _job("after-change-lock-set-on-2-with-4-matching-key-03d49fa.webp"),
    _job("after-front-fence-repair-08fc100.webp"),
    _job("after-laminate-lvp-installation-d86a9bf.webp"),
    _job("Refinished_Bathroom.webp"),
    _job("Refinished_Room2.webp"),
    _job("after-transition-strip-98fcc0e.webp"),
    _job("after-clean-exterior-front-of-house-70a4580.webp"),
    "/Images/Knight-Hammer.webp",
    "/Images/cities/safety-harbor.webp",
)

_GRID_RE = re.compile(r'(<div class="kg-service-related-grid">)(.*?)(</div>)', re.S)
_CARD_RE = re.compile(
    r'<a class="kg-service-related-card(?:\s+kg-service-related-card--face)?" href="([^"]+)">\s*'
    r"<img src=\"[^\"]+\" alt=\"[^\"]*\"[^>]*>\s*"
    r'<span class="kg-service-related-card__label">([^<]*)</span>\s*</a>',
    re.S,
)
_IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.I)


def src_key(src: str) -> str:
    return src.split("?", 1)[0].rstrip("/").lower()


def is_face_card_src(src: str) -> bool:
    key = src_key(src)
    return any(token in key for token in FACE_CARD_TOKENS)


def reset_gallery_cover_cache() -> None:
    global _GALLERY_COVERS
    _GALLERY_COVERS = None


def _disk_file(web_path: str) -> Path:
    return ROOT.joinpath(*web_path.lstrip("/").replace("\\", "/").split("/"))


def _web_path_if_exists(web_path: str) -> str | None:
    return web_path if _disk_file(web_path).is_file() else None


def after_still_web_path(group_id: str) -> str:
    """Related-card still: one after photo, not the before/process/after composite."""
    core = str(group_id).strip().removesuffix("-before-after")
    return f"/GalleryImages/after-{core}.webp"


def _load_gallery_covers() -> dict[str, str]:
    global _GALLERY_COVERS
    if _GALLERY_COVERS is not None:
        return _GALLERY_COVERS
    covers: dict[str, str] = {}
    if GALLERY_MANIFEST.is_file():
        data = json.loads(GALLERY_MANIFEST.read_text(encoding="utf-8"))
        for group in data.get("groups") or []:
            gid = str(group.get("id") or "").strip()
            if not gid:
                continue
            still = after_still_web_path(gid)
            if _web_path_if_exists(still):
                covers[gid] = still
                continue
            for image in group.get("images") or []:
                filename = str(image.get("filename") or "").strip()
                if not filename or "-640w." in filename or "-social." in filename:
                    continue
                src = str(image.get("src") or f"GalleryImages/{filename}").lstrip("/")
                web = f"/{src.replace('\\', '/')}"
                if _web_path_if_exists(web):
                    covers[gid] = web
                    break
    _GALLERY_COVERS = covers
    return covers


def gallery_cover_src(href: str) -> str | None:
    path = href.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if not path.startswith("/gallery/"):
        return None
    return _load_gallery_covers().get(path[len("/gallery/") :])


def related_card_src(href: str) -> str:
    """Return an absolute image path for any related-card destination."""
    path = href.split("#", 1)[0].split("?", 1)[0].rstrip("/") or "/"
    cover = gallery_cover_src(path)
    if cover:
        return cover
    mapped = PAGE_CARD_IMAGES.get(path) or SLUG_CARD_IMAGES.get(related_slug(path))
    if mapped:
        return mapped
    image = resolve_card_image(href)
    if image.startswith("cities/"):
        return f"/Images/{image}"
    return f"/Images/services/{image}"


def _unique_pool() -> list[str]:
    pool: list[str] = []
    seen: set[str] = set()
    for src in (*UNIQUE_FALLBACKS, *_load_gallery_covers().values()):
        key = src_key(src)
        if key in seen or not _web_path_if_exists(src):
            continue
        seen.add(key)
        pool.append(src)
    return pool


def href_topic(href: str) -> str:
    blob = related_slug(href).lower().replace("_", "-")
    for topic, needles in TOPIC_KEYWORDS.items():
        if any(needle in blob for needle in needles):
            return topic
    return "general"


def _candidate_srcs(href: str) -> list[str]:
    preferred = related_card_src(href)
    ordered: list[str] = []
    seen: set[str] = set()
    for src in (preferred, *TOPIC_POOLS.get(href_topic(href), ()), *UNIQUE_FALLBACKS):
        if not _web_path_if_exists(src):
            continue
        key = src_key(src)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(src)
    return ordered


def assign_unique_related_srcs(
    links: list[tuple[str, str]],
    *,
    reserved: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Prefer the topical source, then swap so no two cards (or reserved page images) share a file."""
    used = {src_key(item) for item in (reserved or []) if item}
    assigned: list[tuple[str, str, str]] = []
    for href, label in links:
        src = next(
            (candidate for candidate in _candidate_srcs(href) if src_key(candidate) not in used),
            related_card_src(href),
        )
        used.add(src_key(src))
        assigned.append((href, label, src))
    return assigned


def render_related_cards(
    links: list[tuple[str, str]],
    *,
    version: str,
    reserved: list[str] | None = None,
) -> str:
    rows: list[str] = []
    for href, label, src in assign_unique_related_srcs(links, reserved=reserved):
        safe_label = html.escape(safe_related_label(href, label))
        face = " kg-service-related-card--face" if is_face_card_src(src) else ""
        rows.append(
            f"""                        <a class="kg-service-related-card{face}" href="{href}">
                            <img src="{src}?v={version}" alt="{safe_label}" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">{safe_label}</span>
                        </a>"""
        )
    return "\n".join(rows)


def rewrite_related_grids(html_text: str, *, version: str) -> str:
    """Rebuild related-card images in already-generated HTML without rewriting the rest of the page."""
    pieces: list[str] = []
    last = 0
    for match in _GRID_RE.finditer(html_text):
        reserved = [
            img.group(1)
            for img in _IMG_SRC_RE.finditer(html_text)
            if not (match.start() <= img.start() and img.end() <= match.end())
        ]
        links = [(href, label) for href, label in _CARD_RE.findall(match.group(2))]
        if not links:
            continue
        cards = render_related_cards(links, version=version, reserved=reserved)
        pieces.append(html_text[last : match.start()])
        pieces.append(f"{match.group(1)}\n{cards}\n                    {match.group(3)}")
        last = match.end()
    if not pieces:
        return html_text
    pieces.append(html_text[last:])
    return "".join(pieces)


def _city_slug_from_geo(href_slug: str) -> str | None:
    match = re.fullmatch(r"(.+)-handyman", href_slug)
    return match.group(1) if match else None


def resolve_card_image(href: str) -> str:
    """Pick a card thumbnail for a related link (trade image; optional city override)."""
    slug = related_slug(href)

    if slug in SERVICE_CARD_IMAGES:
        filename = SERVICE_CARD_IMAGES[slug]
        if (SERVICES_IMG_DIR / filename).is_file():
            return filename

    if slug in NICHE_PARENT:
        parent = NICHE_PARENT[slug]
        filename = SERVICE_CARD_IMAGES.get(parent, "handyman.webp")
        if (SERVICES_IMG_DIR / filename).is_file():
            return filename

    city_slug = _city_slug_from_geo(slug)
    if city_slug:
        city_file = CITIES_IMG_DIR / f"{city_slug}.webp"
        if city_file.is_file():
            # Served via render_related cities branch (Images/cities/).
            return f"cities/{city_slug}.webp"

    return "handyman.webp"


def is_service_href(href: str) -> bool:
    return href.startswith("/Services/")


def geo_related_services() -> list[tuple[str, str]]:
    return list(CORE_GEO_RELATED)


def combo_related_services(parent: str, niche_slug: str, service_label: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = [
        (f"/Services/{niche_slug}", service_label.title()),
        (f"/Services/{parent}", PARENT_LABELS.get(parent, parent.replace("-", " ").title())),
    ]
    seen = {related_slug(h) for h, _ in links}
    for href, label in CORE_GEO_RELATED:
        slug = related_slug(href)
        if slug in seen:
            continue
        links.append((href, label))
        seen.add(slug)
        if len(links) >= 4:
            break
    if len(links) < 4:
        extra = PARENT_NICHE_EXTRAS.get(parent)
        if extra and related_slug(extra[0]) not in seen:
            links.append(extra)
    return links[:4]


def pricing_related_services() -> list[tuple[str, str]]:
    return [
        ("/Services/handyman", "Handyman services"),
        ("/Services/plumbing-services", "Plumbing assessment"),
        ("/Services/general-repairs", "General repairs"),
        ("/Services/emergency-services", "Emergency services"),
    ]


def niche_related_fallback(parent: str, slug: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = [
        (f"/Services/{parent}", PARENT_LABELS.get(parent, parent)),
    ]
    extra = PARENT_NICHE_EXTRAS.get(parent)
    if extra and related_slug(extra[0]) != slug:
        links.append(extra)
    for href, label in CORE_GEO_RELATED:
        if len(links) >= 4:
            break
        if related_slug(href) in {related_slug(h) for h, _ in links}:
            continue
        links.append((href, label))
    return links[:4]
