#!/usr/bin/env python3
"""Curated before / process / after media for service, city, and combo pages.

Hash-walking the raw GalleryImages pool put duplicate -640w variants and
off-topic shots (fixture boxes on /Services/handyman) into prose. This catalog
is an allow-list: only inspected, worthy files are eligible, one file per job,
and hub pages get diverse composites instead of one trade.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "GalleryImages"

ROLE_LABELS = {
    "before": "Before",
    "process": "Process",
    "after": "After",
    "composite": "Before · process · after",
    "area": "Service area",
}

# Pages that should show a mix of best, variable jobs — not one trade.
HUB_SLUGS = {
    "handyman",
    "general-repairs",
    "home-repair-near-me",
    "small-jobs",
    "custom-projects",
    "emergency-services",
    "rental-turnover-handyman",
    "property-manager-handyman",
    "hurricane-repair-handyman-pinellas",
    "handyman-scope-florida",
    "safety-harbor-home-repair",
}

COMBO_SERVICE_TOPICS = {
    "sink-repair": ("sink", "plumbing"),
    "drywall-repair": ("drywall",),
    "home-repair": ("hub",),
    "toilet-repair": ("toilet", "plumbing"),
    "door-adjustment": ("door", "lock"),
    "trim-repair": ("carpentry", "floor"),
    "interior-painting": ("paint",),
}

SLUG_TOPICS: dict[str, tuple[str, ...]] = {
    "handyman": ("hub",),
    "general-repairs": ("hub",),
    "home-repair-near-me": ("hub",),
    "small-jobs": ("hub",),
    "custom-projects": ("custom", "carpentry", "cabinet"),
    "emergency-services": ("emergency", "yard", "fence"),
    "electrical-work": ("electrical",),
    "plumbing-services": ("plumbing", "sink", "toilet", "faucet"),
    "carpentry-framing": ("carpentry", "cabinet", "floor", "fence"),
    "doors-windows": ("door", "screen", "blind", "lock"),
    "painting-finishing": ("paint", "drywall"),
    "home-renovations": ("reno", "floor", "drywall"),
    "cabinet-repair": ("cabinet",),
    "custom-shelving": ("cabinet", "carpentry"),
    "small-job-carpenter": ("carpentry", "cabinet", "floor"),
    "trim-repair": ("carpentry",),
    "door-frame-repair": ("door", "lock"),
    "door-adjustment": ("door", "lock"),
    "sliding-door-repair": ("door",),
    "screen-door-repair": ("screen", "door"),
    "window-screen-repair": ("screen",),
    "drywall-repair": ("drywall",),
    "drywall-paint-repair": ("drywall", "paint"),
    "hole-in-wall-repair": ("drywall",),
    "texture-matching": ("drywall", "paint"),
    "interior-painting": ("paint",),
    "trim-painting": ("paint",),
    "water-damage-repair": ("water", "drywall"),
    "caulking-repair": ("caulk",),
    "mobile-home-repairs": ("floor", "carpentry", "hub"),
    "sink-faucet-repair": ("sink", "plumbing"),
    "faucet-replacement": ("faucet", "plumbing"),
    "toilet-repair": ("toilet", "plumbing"),
    "garbage-disposal-replacement": ("disposal", "plumbing"),
    "drain-unclogging": ("sink", "plumbing"),
    "shutoff-valve-repair": ("plumbing", "sink"),
    "plumber-background-handyman": ("plumbing", "sink"),
}

RELATED_TOPICS: dict[str, tuple[str, ...]] = {
    "cabinet": ("cabinet",),
    "carpentry": ("carpentry", "cabinet", "floor", "fence"),
    "door": ("door", "lock", "screen", "blind"),
    "lock": ("lock", "door"),
    "screen": ("screen", "door", "blind"),
    "blind": ("blind", "door"),
    "drywall": ("drywall", "paint", "water"),
    "paint": ("paint", "drywall", "reno"),
    "plumbing": ("plumbing", "sink", "toilet", "faucet"),
    "sink": ("sink", "plumbing", "faucet"),
    "toilet": ("toilet", "plumbing"),
    "faucet": ("faucet", "plumbing", "sink"),
    "floor": ("floor", "carpentry", "reno"),
    "fence": ("fence", "yard", "carpentry"),
    "reno": ("reno", "floor", "drywall", "paint"),
    "water": ("water", "drywall", "plumbing"),
    "caulk": ("caulk", "water"),
    "disposal": ("disposal", "plumbing", "sink"),
    "yard": ("yard", "fence", "emergency"),
    "emergency": ("emergency", "yard", "fence", "hub"),
    "custom": ("custom", "carpentry", "cabinet", "reno"),
    "electrical": ("electrical",),
}


def _entry(
    filename: str,
    *,
    role: str,
    topics: tuple[str, ...],
    alt: str,
    caption: str,
    hub: bool = False,
    slugs: tuple[str, ...] = (),
    job_id: str | None = None,
) -> dict[str, object]:
    stem = filename.rsplit(".", 1)[0].lower()
    return {
        "src": f"GalleryImages/{filename}",
        "filename": filename,
        "role": role,
        "topics": topics,
        "primary": topics[0],
        "alt": alt,
        "caption": caption,
        "hub": hub,
        "slugs": slugs,
        "job_id": job_id or stem,
    }


# Inspected allow-list. Rejected (do not add back):
# AC filter / vent / battery / smoke-alarm / door-wedge / stair-tape /
# fire-extinguisher / curtain-rod / Copeland work order / Screen Team card /
# KITHCHEN and FACUET typos / "YouTube video link" title / truncated hose-bib
# title / empty black grids / comic-font flyers / tub-drain-trim-only /
# raw fixture-junction boxes on hub pages / 640w and social twins.
CATALOG: list[dict[str, object]] = [
    _entry(
        "KnightGroup_Drywall_Panel_Before_After_Original_Photos.webp",
        role="composite",
        topics=("drywall",),
        hub=True,
        alt="Drywall panel opened, patched, and prepped for paint — before and after from a Knight Group job in Pinellas County",
        caption="Wall panel cut out, patched, and mudded for paint",
    ),
    _entry(
        "before-after-ceiling-drywall-patch-2f1127e.webp",
        role="composite",
        topics=("drywall",),
        hub=True,
        alt="Ceiling drywall hole patched and textured — before, process, and after from a Knight Group job in Pinellas County",
        caption="Ceiling opening framed, patched, and blended",
    ),
    _entry(
        "before-after-attic-drywall-return-visit-54b0dce.webp",
        role="composite",
        topics=("drywall",),
        slugs=("drywall-repair", "drywall-paint-repair", "texture-matching"),
        alt="Attic drywall seams taped and mudded on a return visit — Knight Group project in Pinellas County",
        caption="Attic drywall seams finished on a return visit",
    ),
    _entry(
        "KnightGroup_sink_leak_repair_workflow.webp",
        role="composite",
        topics=("sink", "plumbing"),
        hub=True,
        alt="Kitchen sink leak inspected at the drain, trap, and supply lines — Knight Group documents the condition and routes licensed plumbing when required",
        caption="Sink leak inspected at drains, trap, and supply lines",
        slugs=("plumbing-services", "sink-faucet-repair"),
    ),
    _entry(
        "before-after-kitchen-sink-leak.webp",
        role="composite",
        topics=("sink", "plumbing"),
        hub=True,
        alt="Kitchen faucet leak before, under-sink process, and a dry working faucet after — Knight Group job in Pinellas County",
        caption="Faucet base leak found, repaired, and left dry",
        slugs=("plumbing-services", "sink-faucet-repair", "clearwater-sink-repair"),
    ),
    _entry(
        "KnightGroup_before_after_tub_spout.webp",
        role="composite",
        topics=("faucet", "plumbing"),
        alt="Exposed tub pipe replaced with a finished chrome tub spout — Knight Group bathroom closeout in Pinellas County",
        caption="Bare tub stub finished with a chrome spout",
        slugs=("plumbing-services", "faucet-replacement", "sink-faucet-repair"),
    ),
    _entry(
        "before-after-2-toilets-7f8c499.webp",
        role="composite",
        topics=("toilet", "plumbing"),
        alt="Two toilets serviced — tank internals and bowl shown before, during, and after. Knight Group documents conditions and routes licensed plumbing when required",
        caption="Two toilets opened, serviced, and closed out",
        slugs=("plumbing-services", "toilet-repair", "largo-toilet-repair"),
    ),
    _entry(
        "before-after-shower-2cf7af0.webp",
        role="composite",
        topics=("faucet", "plumbing"),
        alt="Shower valve handle and cartridge replaced — before, process, and after from a Knight Group bathroom job in Pinellas County",
        caption="Shower handle and cartridge replaced",
        slugs=("plumbing-services", "faucet-replacement"),
    ),
    _entry(
        "before-after-handyman-repair-e8e763c.webp",
        role="composite",
        topics=("toilet", "plumbing"),
        alt="Toilet trip-lever and tank handle replaced — before and after from a Knight Group job in Pinellas County",
        caption="Broken toilet handle and tank linkage replaced",
        slugs=("toilet-repair", "plumbing-services"),
    ),
    _entry(
        "OldTubDrain.webp",
        role="before",
        topics=("plumbing",),
        job_id="tub-drain-replacement",
        alt="Failed tub drain assembly before replacement — Knight Group documents the condition and routes licensed plumbing when required",
        caption="Original tub drain that needed replacement",
        slugs=("plumbing-services", "drain-unclogging"),
    ),
    _entry(
        "NewTubDrain.webp",
        role="after",
        topics=("plumbing",),
        job_id="tub-drain-replacement",
        alt="New tub drain installed after the failed assembly was replaced — Knight Group bathroom closeout in Pinellas County",
        caption="New tub drain installed",
        slugs=("plumbing-services", "drain-unclogging"),
    ),
    _entry(
        "GarbageDisposal.webp",
        role="after",
        topics=("disposal", "plumbing"),
        alt="Garbage disposal in place under a kitchen sink — Knight Group documents the unit and routes licensed connections when required",
        caption="Disposal in place after the under-sink closeout",
        slugs=("garbage-disposal-replacement", "plumbing-services"),
    ),
    _entry(
        "KnightGroup_before_progress_after_shutter_doors.webp",
        role="composite",
        topics=("door",),
        hub=True,
        alt="Bi-fold shutter doors realigned — before, track and guide process, and finished doors from a Knight Group job in Pinellas County",
        caption="Sagging bi-fold shutters tracked, guided, and squared",
    ),
    _entry(
        "before-after-door-lock.webp",
        role="composite",
        topics=("lock", "door"),
        hub=True,
        alt="Forced door-frame damage repaired and lockset replaced — before, process, and after from a Knight Group job in Pinellas County",
        caption="Splintered strike-side frame repaired and rekeyed",
    ),
    _entry(
        "KnightGroup_screen_panel_repair_corrected.webp",
        role="composite",
        topics=("screen",),
        hub=True,
        alt="Patio screen panel replaced — before the missing mesh and after the taut new panel, Knight Group job in Pinellas County",
        caption="Missing patio screen panel replaced",
    ),
    _entry(
        "before-after-resecure-loose-screen-door.webp",
        role="composite",
        topics=("screen", "door"),
        alt="Loose screen door pulled back to the frame and resecured — before and after from a Knight Group job in Pinellas County",
        caption="Screen door pulled back and fastened to the frame",
        slugs=("screen-door-repair", "doors-windows", "window-screen-repair"),
    ),
    _entry(
        "before-after-blind-repair.webp",
        role="composite",
        topics=("blind",),
        hub=True,
        alt="Broken horizontal blinds restrung and leveled — before and after from a Knight Group job in Pinellas County",
        caption="Sagging slats restrung so the blind hangs level",
    ),
    _entry(
        "before-after-kitchen-window-blinds-repair.webp",
        role="composite",
        topics=("blind",),
        alt="Kitchen window blinds remounted — empty frame before, brackets during, and level blinds after, Knight Group job in Pinellas County",
        caption="Kitchen blinds remounted on new brackets",
        slugs=("doors-windows", "window-screen-repair"),
    ),
    _entry(
        "before-after-broken-blinds-replaced.webp",
        role="composite",
        topics=("blind",),
        alt="Broken window blinds replaced — before and after from a Knight Group job in Pinellas County",
        caption="Broken blinds taken down and replaced",
        slugs=("doors-windows"),
    ),
    _entry(
        "before-after-cabinet-repair-339b0d9.webp",
        role="composite",
        topics=("cabinet",),
        hub=True,
        alt="Bathroom vanity drawer off its tracks rebuilt and rehung — before, process, and after from a Knight Group job in Pinellas County",
        caption="Fallen vanity drawer rebuilt and rehung",
    ),
    _entry(
        "before-after-fence-repair.webp",
        role="composite",
        topics=("fence",),
        hub=True,
        alt="Leaning wood fence straightened — before and after from a Knight Group job in Pinellas County",
        caption="Leaning wood fence posts reset and the run straightened",
    ),
    _entry(
        "before-after-side-yard-gate-repair-18bb381.webp",
        role="composite",
        topics=("fence",),
        alt="Side-yard gate repaired so it hangs and latches — Knight Group job in Pinellas County",
        caption="Side-yard gate rehung and latched",
        slugs=("carpentry-framing", "emergency-services"),
    ),
    _entry(
        "before-after-laminate-lvp-installation-d86a9bf.webp",
        role="composite",
        topics=("floor", "reno"),
        hub=True,
        alt="Worn carpet pulled and laminate LVP installed — before, process, and after from a Knight Group job in Pinellas County",
        caption="Carpet out, laminate LVP laid, transition closed",
    ),
    _entry(
        "Fixing_floor.webp",
        role="process",
        topics=("floor", "water"),
        job_id="floor-subfloor-repair",
        alt="Rotted floor opened to the subfloor during a Knight Group repair in Pinellas County",
        caption="Damaged floor opened back to sound framing",
        slugs=("carpentry-framing", "water-damage-repair", "mobile-home-repairs"),
    ),
    _entry(
        "fixing_floor2.webp",
        role="before",
        topics=("floor", "water"),
        job_id="floor-subfloor-repair",
        alt="Floor and base trim opened for a subfloor repair — Knight Group job in Pinellas County",
        caption="Tile and base opened at the damaged run",
        slugs=("carpentry-framing", "water-damage-repair", "mobile-home-repairs"),
    ),
    _entry(
        "Window_Wall.webp",
        role="before",
        topics=("water", "drywall"),
        job_id="window-wall-repair",
        alt="Window-wall damage opened so wet material could be removed — Knight Group job in Pinellas County",
        caption="Window wall opened after moisture damage",
        slugs=("water-damage-repair", "drywall-repair"),
    ),
    _entry(
        "Window_Wall2.webp",
        role="process",
        topics=("water", "drywall"),
        job_id="window-wall-repair",
        alt="Window framed and a new sill set during wall rebuild — Knight Group process photo in Pinellas County",
        caption="New sill and framing set at the window opening",
        slugs=("water-damage-repair", "drywall-repair"),
    ),
    _entry(
        "Moldy_Wall.webp",
        role="before",
        topics=("water",),
        job_id="mold-wall-repair",
        alt="Mold-stained interior wall before correction — Knight Group documents the condition in Pinellas County",
        caption="Mold staining on the wall before tear-out",
        slugs=("water-damage-repair"),
    ),
    _entry(
        "Moldy_Wall2.webp",
        role="process",
        topics=("water",),
        job_id="mold-wall-repair",
        alt="Later stage of a mold-wall correction — Knight Group process photo in Pinellas County",
        caption="Same wall after the damaged face was cut back",
        slugs=("water-damage-repair"),
    ),
    _entry(
        "before-after-recaulk-around-kitchen-windowsill-custom-5cca131.webp",
        role="composite",
        topics=("caulk",),
        alt="Failed kitchen windowsill caulk cut out and a clean bead tooled — before and after from a Knight Group job in Pinellas County",
        caption="Failed sill caulk cut out and tooled clean",
        slugs=("caulking-repair",),
    ),
    _entry(
        "Refinishing_Bathroom_Window2.webp",
        role="process",
        topics=("reno",),
        hub=True,
        alt="Bathroom remodel in process — tub tile, vanity, and floor work by Knight Group in Pinellas County",
        caption="Bathroom tile, vanity, and floor underway",
        slugs=("home-renovations",),
    ),
    _entry(
        "Refinished Bathroom_Window.webp",
        role="after",
        topics=("reno",),
        job_id="bathroom-tub-window-remodel",
        alt="Finished bathroom tub surround, window, and floor remodel by Knight Group in Pinellas County",
        caption="Tub surround, window, and floor closed out",
        slugs=("home-renovations",),
    ),
    _entry(
        "Refinished_Bathroom.webp",
        role="process",
        topics=("reno",),
        job_id="bathroom-remodel-cobblestone",
        alt="Bathroom remodel with pebble shower floor and vanity set — Knight Group project in Pinellas County",
        caption="Shower tile, vanity, and plank floor in place",
        slugs=("home-renovations",),
    ),
    _entry(
        "Refinished_Room2.webp",
        role="after",
        topics=("paint", "reno"),
        alt="Interior room after refinish — walls, trim, and a cleaner closeout by Knight Group in Pinellas County",
        caption="Room refinished and ready to live in",
        slugs=("interior-painting", "painting-finishing", "home-renovations", "trim-painting"),
    ),
    _entry(
        "Refinished_Room.webp",
        role="after",
        topics=("paint",),
        job_id="room-refinish",
        alt="First view of a refinished interior room by Knight Group in Pinellas County",
        caption="Fresh walls after the room refinish",
        slugs=("interior-painting", "painting-finishing"),
    ),
    _entry(
        "KnightGroup_before_after_agave_removal.webp",
        role="composite",
        topics=("yard", "emergency"),
        hub=True,
        alt="Large agave cut down and the yard cleaned — before, process, and finished site from a Knight Group job in Pinellas County",
        caption="Overgrown agave removed and the pad cleaned",
        slugs=("emergency-services", "custom-projects", "hurricane-repair-handyman-pinellas"),
    ),
    _entry(
        "before-after-handyman-repair-2ef83e1.webp",
        role="composite",
        topics=("custom", "carpentry"),
        alt="Torn furniture frame opened and a new support set — before, process, and structural after from a Knight Group job in Pinellas County",
        caption="Broken furniture rail opened and a new support set",
        slugs=("custom-projects", "small-job-carpenter"),
    ),
    _entry(
        "before-after-handyman-repair-23ebf3d.webp",
        role="composite",
        topics=("electrical",),
        alt="Historical light-fixture and fan project photos; current electrical installation is referred to a licensed electrician",
        caption="Historical fixture work — new installs go to a licensed electrician",
        slugs=("electrical-work",),
    ),
    _entry(
        "before-after-handyman-repair-163b4a6.webp",
        role="composite",
        topics=("electrical",),
        alt="Historical ceiling-fan replacement photos; current electrical installation is referred to a licensed electrician",
        caption="Historical fan swap — new wiring is referred out",
        slugs=("electrical-work",),
    ),
    _entry(
        "before-after-office-ceiling-fan-malfunction.webp",
        role="composite",
        topics=("electrical",),
        alt="Historical office ceiling-fan repair photos; current electrical installation is referred to a licensed electrician",
        caption="Historical office fan repair — licensed electrician for new work",
        slugs=("electrical-work",),
    ),
]


def _file_exists(filename: str) -> bool:
    return (GALLERY_DIR / filename).is_file()


def available_catalog() -> list[dict[str, object]]:
    return [item for item in CATALOG if _file_exists(str(item["filename"]))]


def _city_slugs() -> set[str]:
    try:
        from seo_page_data import COUNTY_REGIONS

        return {city["slug"] for region in COUNTY_REGIONS for city in region["cities"]}
    except Exception:
        return set()


def is_hub_slug(slug: str) -> bool:
    if slug in HUB_SLUGS:
        return True
    if slug.endswith("-handyman") and not slug.startswith("pricing-"):
        return True
    return False


def topics_for_slug(slug: str) -> tuple[str, ...]:
    if slug in SLUG_TOPICS:
        return SLUG_TOPICS[slug]
    if is_hub_slug(slug):
        return ("hub",)
    cities = _city_slugs()
    for city in sorted(cities, key=len, reverse=True):
        prefix = f"{city}-"
        if slug.startswith(prefix):
            service = slug[len(prefix) :]
            if service in COMBO_SERVICE_TOPICS:
                return COMBO_SERVICE_TOPICS[service]
            if service in SLUG_TOPICS:
                return SLUG_TOPICS[service]
    parent = slug.rsplit("-", 1)[0] if "-" in slug else slug
    if parent in SLUG_TOPICS:
        return SLUG_TOPICS[parent]
    return ("hub",)


def _topic_score(item: dict[str, object], topics: set[str], slug: str) -> tuple:
    item_topics = set(item["topics"])
    slugs = set(item.get("slugs") or ())
    explicit = 0 if slug in slugs else 1
    overlap = len(item_topics & topics)
    hub_bonus = 0 if (item.get("hub") and "hub" in topics) else 1
    still = 0 if item["role"] == "composite" else 1
    return (explicit, still, hub_bonus, -overlap, str(item["job_id"]))


def _matches(item: dict[str, object], topics: set[str], slug: str, *, hub: bool) -> bool:
    if slug in set(item.get("slugs") or ()):
        return True
    item_topics = set(item["topics"])
    if hub:
        return bool(item.get("hub")) or bool(item_topics & {"hub"})
    if "electrical" in topics:
        return "electrical" in item_topics
    return bool(item_topics & topics)


def _related_topics(topics: tuple[str, ...]) -> set[str]:
    related: set[str] = set(topics)
    for topic in topics:
        related.update(RELATED_TOPICS.get(topic, ()))
    return related


HUB_ROTATE_ORDER = [
    "handyman",
    "general-repairs",
    "home-repair-near-me",
    "small-jobs",
    "custom-projects",
    "emergency-services",
    "rental-turnover-handyman",
    "property-manager-handyman",
    "hurricane-repair-handyman-pinellas",
    "handyman-scope-florida",
    "safety-harbor-home-repair",
]


def _rotation_start(slug: str, size: int) -> int:
    if size <= 1:
        return 0
    if slug in HUB_ROTATE_ORDER:
        return (HUB_ROTATE_ORDER.index(slug) * 2) % size
    if slug.endswith("-handyman"):
        city = slug[: -len("-handyman")]
        cities = sorted(_city_slugs())
        if city in cities:
            return cities.index(city) % size
    digest = hashlib.sha256(f"kg-media::{slug}".encode("utf-8")).hexdigest()
    return int(digest, 16) % size


def _rotate(items: list[dict[str, object]], slug: str) -> list[dict[str, object]]:
    if len(items) <= 1:
        return items
    start = _rotation_start(slug, len(items))
    return items[start:] + items[:start]


def _diversify(items: list[dict[str, object]], count: int) -> list[dict[str, object]]:
    picked: list[dict[str, object]] = []
    used_jobs: set[str] = set()
    used_primary: set[str] = set()

    def take(predicate) -> None:
        for item in items:
            if len(picked) >= count:
                return
            job = str(item["job_id"])
            if job in used_jobs:
                continue
            if not predicate(item):
                continue
            picked.append(item)
            used_jobs.add(job)
            used_primary.add(str(item["primary"]))

    take(lambda item: str(item["primary"]) not in used_primary)
    take(lambda _item: True)
    return picked[:count]


def _prefer_progression(matched: list[dict[str, object]], count: int) -> list[dict[str, object]] | None:
    """Use a before/process/after still set only when topical composites are scarce."""
    composites = [item for item in matched if item["role"] == "composite"]
    if len(composites) >= count:
        return None
    by_job: dict[str, list[dict[str, object]]] = {}
    for item in matched:
        if item["role"] in {"before", "process", "after"}:
            by_job.setdefault(str(item["job_id"]), []).append(item)
    for job_id, group in by_job.items():
        roles = {str(item["role"]) for item in group}
        if "before" in roles and ("after" in roles or "process" in roles) and len(group) >= 2:
            order = {"before": 0, "process": 1, "after": 2}
            story = sorted(group, key=lambda item: order.get(str(item["role"]), 9))
            combined = composites + story
            if len(combined) >= min(2, count):
                return _diversify(combined, count)
    return None


def pick_curated_images(slug: str, count: int = 4) -> list[dict[str, str]]:
    catalog = available_catalog()
    if not catalog or count <= 0:
        return []

    topics = topics_for_slug(slug)
    topic_set = set(topics)
    hub = is_hub_slug(slug) or topics == ("hub",)

    matched = [item for item in catalog if _matches(item, topic_set, slug, hub=hub)]
    if not matched and not hub:
        related = _related_topics(topics)
        matched = [item for item in catalog if set(item["topics"]) & related and "electrical" not in item["topics"]]
    if not matched:
        matched = [item for item in catalog if item.get("hub")]

    matched.sort(key=lambda item: _topic_score(item, topic_set, slug))

    if hub:
        heroes = [item for item in matched if item.get("hub")] or matched
        heroes = _rotate(heroes, slug)
        chosen = _diversify(heroes, count)
    else:
        story = _prefer_progression(matched, count)
        chosen = story if story else _diversify(matched, count)
        if len(chosen) < count:
            related = _related_topics(topics)
            extras = [
                item
                for item in catalog
                if item not in chosen
                and str(item["job_id"]) not in {str(x["job_id"]) for x in chosen}
                and set(item["topics"]) & related
                and "electrical" not in item["topics"]
            ]
            chosen = _diversify(chosen + extras, count)

    payload: list[dict[str, str]] = []
    for item in chosen:
        payload.append(
            {
                "src": str(item["src"]),
                "alt": str(item["alt"]),
                "role": str(item["role"]),
                "caption": str(item["caption"]),
                "category": str(item["primary"]),
            }
        )
    return payload
