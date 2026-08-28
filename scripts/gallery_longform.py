"""Unique 750+ word copy for Knight Group gallery project pages.

Each composite job gets its own phrasing from the catalog facts (worker, city,
month, notes, photo counts) plus a slug-seeded voice. Ticket prices, streets,
customer phones, and vendor names are never interpolated.
"""
from __future__ import annotations

import hashlib
import html
import random
import re
from typing import Any

from gallery_detail_copy import gallery_body_extra
from gallery_public_web import sanitize_page_text, strip_html_words

KG_PHONE = "(813) 649-3341"
MIN_WORDS = 750

_CLUSTER_NEEDLES: list[tuple[str, tuple[str, ...]]] = [
    ("fence", ("fence", "picket", "privacy panel")),
    ("screen", ("screen door", "rescreen", "patio screen")),
    ("blinds", ("blind", "shade")),
    ("door_lock", ("lock", "deadbolt", "latch", "strike")),
    ("drywall", ("drywall", "sheetrock", "wall hole", "texture", "ceiling patch")),
    ("paint", ("paint", "primer")),
    ("caulk", ("caulk", "caulking")),
    ("filter_hvac", ("filter", "hvac", "ac vent", "air return")),
    ("sink_drain", ("sink", "drain", "disposal")),
    ("toilet", ("toilet",)),
    ("faucet", ("faucet",)),
    ("fan", ("ceiling fan", "fan")),
    ("electrical_fixture", ("outlet", "switch", "ballast", "light fixture")),
    ("floor", ("floor", "subfloor", "carpet")),
    ("hardware", ("curtain", "grab bar", "extinguisher", "wedge", "shelf")),
]


def infer_cluster(title: str, explicit: str = "") -> str:
    if explicit:
        return explicit
    lower = (title or "").lower()
    for cluster, needles in _CLUSTER_NEEDLES:
        if any(needle in lower for needle in needles):
            return cluster
    return "general"


def _esc(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=True)


def _seed(slug: str) -> random.Random:
    digest = hashlib.sha256(slug.encode("utf-8")).hexdigest()
    return random.Random(int(digest, 16))


def _pick(rng: random.Random, options: list[str]) -> str:
    return options[rng.randrange(len(options))]


def _take(rng: random.Random, options: list[str], count: int) -> list[str]:
    pool = list(options)
    rng.shuffle(pool)
    return pool[: max(1, min(count, len(pool)))]


def city_href(slug: str) -> str:
    if slug == "lutz":
        return "/hillsborough-handyman"
    return f"/{slug}-handyman" if slug else ""


def county_href(county: str) -> str:
    if "Pasco" in county:
        return "/pasco-handyman"
    if "Hillsborough" in county:
        return "/hillsborough-handyman"
    return "/pinellas-handyman"


def place_label(group: dict) -> str:
    city = str(group.get("cityName") or "").strip()
    county = str(group.get("countyName") or "Pinellas County").strip()
    if city:
        return f"{city}, {county}"
    return county


CLUSTERS: dict[str, dict[str, Any]] = {
    "fence": {
        "label": "fence repair",
        "service": ("/Services/carpentry-framing", "carpentry and framing"),
        "keywords": [
            "fence repair",
            "leaning fence",
            "wood fence repair",
            "fence post repair",
            "privacy fence repair",
            "storm-damaged fence",
        ],
        "openings": [
            "{place} yards take a beating from sandy soil, afternoon downpours, and wind that finds the tallest privacy run on the property. This visit was a {title_lower} job: the line had already moved past a cosmetic lean and needed to stand plumb again.",
            "A fence that walks off the post line is a security problem before it is a curb-appeal problem. Homeowners in {place} called Knight Group for {title_lower} after panels started to rack and the yard no longer closed.",
            "Florida wood fences fail at the ground first. This {title_lower} project in {place} started with posts that had lost bearing, then rails and pickets that followed the lean.",
        ],
        "search": [
            "In the Tampa Bay search market, homeowners keep looking up fence repair, leaning fence, and wood fence repair through hurricane season and the humid months after. Interest does not vanish in winter here the way it does in freeze climates, because soil movement and post rot do not take a season off.",
            "Queries such as privacy fence repair and fence post repair stay useful in Pinellas, Hillsborough, and Pasco because a single failed post can open a whole backyard. This page is written around those phrases without pretending a national ranking.",
            "Storm-damaged fence searches spike after named storms, but the everyday job in {county} is quieter: a section that drifted after rain, a gate that no longer meets, or pickets that pulled their fasteners.",
        ],
        "methods": [
            ("Document the failed run", "Photograph the lean, the post bases, and any gate hardware before anything is pulled apart so the owner can see why the section moved."),
            ("Relieve the load", "Support or unfasten racked panels so remaining posts are not forced further out of plumb while the failed members come out."),
            ("Reset structure", "Replace or reset posts that have lost bearing, then rebuild rails so pickets can land on a straight, fastened line."),
            ("Reattach the skin", "Refasten pickets or panels to the corrected frame, matching spacing where the existing run is still sound."),
            ("Prove the close", "Check plumb, latch, and neighbor-side appearance, then leave before-and-after photos on the ticket."),
        ],
        "climate": [
            "West-central Florida soil does not hold a shallow post the way clay up north does. Add termite pressure and year-round moisture at grade, and wood fence posts often rot in a band you cannot see until the panel walks.",
            "South- and west-facing runs take more UV, so rails check and split even when posts still look fair from the driveway. Repair beats full replacement when the failure is still isolated.",
        ],
        "aftercare": [
            "Keep soil and irrigation off the post bases, and recaulk or reseal cut ends if you add a stain later. Call if a neighboring section starts to follow the same lean.",
            "A repaired run still lives in Florida weather. Watch the gate after the next hard rain; hardware that was reset should stay true, and new movement is a reason to send a photo.",
        ],
    },
    "screen": {
        "label": "screen door repair",
        "service": ("/Services/doors-windows", "doors and windows"),
        "keywords": [
            "screen door repair",
            "rescreen patio",
            "loose screen door",
            "pool cage screen",
            "sliding screen repair",
        ],
        "openings": [
            "Gulf air and slamming use loosen screen-door frames faster than most hardware is designed for. This {title_lower} visit in {place} was about getting the door to close, latch, and keep bugs out again.",
            "A screen that has walked off its track or pulled out of the spline groove is a daily irritation in {place}. Knight Group treated this as {title_lower}, not a full enclosure rebuild.",
            "Patio and entry screens in {county} fail at corners, rollers, and splines. The photos on this page are from a completed {title_lower} job.",
        ],
        "search": [
            "Screen door repair and rescreen patio remain steady searches across Tampa Bay because enclosures are part of how people live outside. Homeowners look for a crew that can resecure a door without quoting a brand-new cage.",
            "Loose screen door and sliding screen repair show up when rollers flatten or the frame twists. Those phrases describe this job more accurately than a generic handyman listing.",
        ],
        "methods": [
            ("Inspect the frame", "Check square, spline condition, roller wear, and latch alignment before cutting new screen or driving fasteners."),
            ("Resecure or respline", "Reset the frame, replace failed spline or mesh where needed, and keep tension even so the panel does not oil-can."),
            ("Restore the close", "Adjust rollers or hinges so the door meets the strike without dragging on the sill."),
            ("Verify insect seal", "Confirm gaps are closed at the latch side and that the owner can operate the door with one hand."),
        ],
        "climate": [
            "Salt air and pool chemistry attack aluminum fasteners. Stainless or coated hardware lasts longer on waterfront and pool-cage doors than the original painted screws.",
        ],
        "aftercare": [
            "Avoid high-pressure washing the new spline. A garden hose and a soft brush keep mesh open without driving water into the frame.",
        ],
    },
    "blinds": {
        "label": "window blind repair",
        "service": ("/Services/doors-windows", "doors and windows"),
        "keywords": ["window blind repair", "blinds replacement", "broken blinds", "plantation shutter repair"],
        "openings": [
            "Pinellas rentals and owner-occupied homes chew through blinds at the same failure points: bent headrails, failed tilters, and brackets that pulled from drywall. This {title_lower} job in {place} put a working covering back on the opening.",
        ],
        "search": [
            "Broken blinds and blinds replacement stay common search phrases because Florida sun fades slats and kids and pets finish the rest. A measured swap is usually faster than hunting one replacement slat for a discontinued product.",
        ],
        "methods": [
            ("Measure the opening", "Confirm inside or outside mount, width, and height before the old covering comes down."),
            ("Remove failed hardware", "Pull bent headrails and stripped brackets without tearing surrounding drywall or trim."),
            ("Install level", "Hit framing where possible, level the headrail, and test raise, lower, and tilt."),
            ("Cord and child-safety check", "Confirm the covering operates cleanly and that excess cord is managed."),
        ],
        "climate": ["South-facing rooms cook inexpensive vinyl. Better brackets and a level headrail matter more than matching a faded color exactly."],
        "aftercare": ["Operate the covering daily for a week and send a photo if a slat binds; most bind issues are a bracket that settled."],
    },
    "door_lock": {
        "label": "door lock repair",
        "service": ("/Services/doors-windows", "doors and windows"),
        "keywords": ["door lock repair", "door will not latch", "deadbolt alignment", "strike plate adjustment"],
        "openings": [
            "A door that will not latch is not a locksmith mystery in most {place} houses — the slab moved, the strike missed, or the latch worn until it only caught on the second slam. This {title_lower} visit restored a clean close.",
        ],
        "search": [
            "Door lock repair and door will not latch stay high-intent phrases because people feel unsafe the same afternoon the latch starts to miss. Deadbolt alignment searches often mean the same job: hardware that no longer meets the jamb.",
        ],
        "methods": [
            ("Diagnose the miss", "Check hinge sag, latch height, and strike location with the door closed slowly, not slammed."),
            ("Correct the geometry", "Shim or tighten hinges, relocate the strike, or replace a worn latch so the bolt throws fully."),
            ("Test keys and privacy", "Confirm key operation, interior thumbturn, and that the door does not self-open."),
            ("Document the result", "Leave photos of the aligned latch and any replaced hardware."),
        ],
        "climate": ["Florida humidity swells wood slabs seasonally. A lock that worked in January can miss in August without anyone damaging the set."],
        "aftercare": ["If the door starts to rub after a rain week, send a short video of the close before the strike tears out again."],
    },
    "drywall": {
        "label": "drywall repair",
        "service": ("/Services/drywall-repair", "drywall repair"),
        "keywords": ["drywall repair", "hole in wall", "ceiling crack repair", "texture match"],
        "openings": [
            "This {title_lower} project in {place} was a wall or ceiling that had already gone past a nail pop: open board, bad tape, or a patch that telegraphed through paint.",
        ],
        "search": [
            "Drywall repair and hole in wall searches in Florida often hide a moisture story. Texture match matters here because knockdown and skip-trowel are more common than smooth Level 5 walls.",
        ],
        "methods": [
            ("Open to sound board", "Cut back to clean paper and framing rather than floating mud over a soft or stained area."),
            ("Replace and tape", "Install patch board, tape joints, and build coats that can take texture."),
            ("Texture and prime", "Match the surrounding pattern as closely as the existing wall allows, then prime so paint can hide the repair."),
            ("Paint-ready handoff", "Leave the area sanded and clean; final color coat follows the written scope."),
        ],
        "climate": ["Humidity slows mud cure. Rushing a ceiling patch in August is how seams flash later."],
        "aftercare": ["Wait for primer to dry fully before judging color. Flash is usually a paint film issue, not a failed patch."],
    },
    "paint": {
        "label": "interior painting repair",
        "service": ("/Services/painting-finishing", "painting and finishing"),
        "keywords": ["interior painting", "touch-up paint", "wall paint repair"],
        "openings": [
            "Paint work on this {title_lower} job in {place} was not a whole-house repaint. It was the finish that makes a repair disappear after carpentry or drywall closed.",
        ],
        "search": [
            "Interior painting searches in Tampa Bay split between full rooms and small repair blending. Homeowners looking at this gallery usually need the second: a patch that does not announce itself under kitchen light.",
        ],
        "methods": [
            ("Protect and prep", "Mask adjacent finishes and sand the repair flush before any color goes on."),
            ("Prime the repair", "Seal patches so sheen and color do not flash."),
            ("Apply finish coats", "Roll or brush to the break lines in the written scope, not past them."),
            ("Walk the light", "Check the wall at an angle before calling the coat done."),
        ],
        "climate": ["Air conditioning vents can skin a coat too fast. Work away from a blasting register when possible."],
        "aftercare": ["Avoid washing the new film for two weeks. Send a photo in natural light if a halo remains."],
    },
    "caulk": {
        "label": "caulking repair",
        "service": ("/Services/caulking-repair", "caulking repair"),
        "keywords": ["caulking repair", "recaulk tub", "toilet caulk", "bathroom caulk"],
        "openings": [
            "Failed caulk in {place} is how bathrooms advertise older leaks. This {title_lower} visit cut out the old joint, cleaned the substrate, and tooled a joint that can actually close.",
        ],
        "search": [
            "Caulking repair, recaulk tub, and toilet caulk remain workhorse searches because silicone that was never tooled, or that sat on soap scum, peels in a season.",
        ],
        "methods": [
            ("Remove the failed joint", "Cut and scrape old material instead of laying a new bead on top of a dirty bond."),
            ("Clean and dry", "Solvent or soap cleanup, then dry time so the new sealant can wet the surface."),
            ("Tool a continuous bead", "Match the joint size to the gap, not a decorative smear."),
            ("Cure before use", "Keep the area dry for the manufacturer window listed on the tube."),
        ],
        "climate": ["Florida bathrooms rarely dry between showers. A joint that is not fully tooled fails twice as fast."],
        "aftercare": ["Skip bleach soaks on fresh silicone. Mild soap is enough for the first month."],
    },
    "filter_hvac": {
        "label": "AC filter and vent service",
        "service": ("/Services/general-repairs", "general repairs"),
        "keywords": ["AC filter replacement", "HVAC filter change", "dirty air return", "vent grille repair"],
        "openings": [
            "Restricted return air is a quiet {place} problem until the filter is actually pulled. This {title_lower} job replaced loaded media and reseated the grille so the system could breathe.",
        ],
        "search": [
            "AC filter replacement and HVAC filter change searches stay year-round in Florida because systems run more hours. Dirty air return photos convince owners the media was past due.",
        ],
        "methods": [
            ("Read the slot", "Confirm size and airflow direction from the old filter or the cabinet label."),
            ("Remove loaded media", "Bag the old filter so dust does not dump into the living space."),
            ("Install the replacement", "Seat the new filter fully so air cannot bypass the media."),
            ("Resecure the grille", "Tighten or replace fasteners so the return cover does not rattle."),
        ],
        "climate": ["Coastal homes load filters faster. A 90-day reminder is often too long in summer."],
        "aftercare": ["Write the install month on the filter frame. Send a photo if the next change looks gray in weeks — that can mean a return leak."],
    },
    "sink_drain": {
        "label": "sink and drain assessment",
        "service": ("/Services/sink-faucet-repair", "sink and faucet problem assessment"),
        "keywords": ["kitchen sink leak", "clogged sink drain", "p-trap replacement", "garbage disposal issue"],
        "openings": [
            "Under-sink water in {place} is a cabinet-destroyer if it sits. This {title_lower} page documents how Knight Group assessed the leak or drain, completed eligible finish work, and routed licensed plumbing when the scope required it.",
        ],
        "search": [
            "Kitchen sink leak and clogged sink drain searches are urgent for a reason. Homeowners want the drip stopped and the cabinet dried, not a lecture. Knight Group quotes what it can lawfully complete and brings in a licensed plumber when the potable connection requires it.",
        ],
        "methods": [
            ("Find the wet path", "Dry the cabinet, run water, and mark whether the leak is trap, disposal, supply, or basket."),
            ("Complete eligible work", "Replace accessible trap parts or reset hardware that stays inside handyman finish scope."),
            ("Route licensed work", "Stop and document if a permitted or licensed potable repair is required."),
            ("Protect the cabinet", "Wipe standing water and photograph the dry closeout."),
        ],
        "climate": ["Florida cabinets wick water into particle board overnight. Photos from the first hour matter."],
        "aftercare": ["Leave the doors open to dry. Call the same day if the stain returns — that is a new leak, not residual moisture."],
    },
    "toilet": {
        "label": "toilet problem assessment",
        "service": ("/Services/toilet-repair", "toilet problem assessment"),
        "keywords": ["running toilet", "toilet leak", "toilet caulk", "loose toilet"],
        "openings": [
            "A running or leaking toilet in {place} wastes water and can stain the floor long before anyone looks at the wax ring. This {title_lower} visit documented the symptom, completed eligible reset or finish work, and routed licensed plumbing when needed.",
        ],
        "search": [
            "Running toilet and toilet leak searches stay constant because flappers and fill valves fail on a timer. Loose toilet searches often mean the closet bolts or the flange, which is where licensed routing starts if the floor is involved.",
        ],
        "methods": [
            ("Identify the symptom", "Separate fill-valve run, flapper leak, base weep, and supply drip before parts come out."),
            ("Eligible reset or finish", "Complete caulk, accessible hardware, or documented closeout inside handyman scope."),
            ("Licensed routing", "Hand off flange, rough-in, or potable work that requires a licensed plumber."),
            ("Verify the close", "Confirm the bowl is stable and the owner knows what was completed versus referred."),
        ],
        "climate": ["Hard water in parts of Tampa Bay shortens fill-valve life. A quiet run at night is still a leak."],
        "aftercare": ["No heavy cleaners around a fresh base bead. Dye-test the tank if the run returns."],
    },
    "faucet": {
        "label": "faucet problem assessment",
        "service": ("/Services/sink-faucet-repair", "sink and faucet problem assessment"),
        "keywords": ["leaky faucet", "kitchen faucet repair", "bathroom faucet drip"],
        "openings": [
            "A drip in {place} is loud at night and expensive over a month. This {title_lower} page shows the assessment and any eligible fixture or finish work Knight Group completed, with licensed plumbing routed when the connection required it.",
        ],
        "search": [
            "Leaky faucet and kitchen faucet repair remain classic searches. Many calls are cartridges; some are supply lines or valves that a licensed plumber must handle.",
        ],
        "methods": [
            ("Map the drip", "Note whether water appears at the spout, handle, supply, or under the deck."),
            ("Eligible fixture work", "Replace accessible trim or document the failed part for the owner."),
            ("Stop for licensed scope", "Do not open potable connections that require a licensed contractor."),
            ("Cleanup", "Dry the cabinet or vanity and photograph the result."),
        ],
        "climate": ["Mineral deposits freeze cartridges. A faucet that suddenly gets stiff is often a week from dripping."],
        "aftercare": ["Use the aerator screen monthly. Send a photo if the drip returns at the same handle."],
    },
    "fan": {
        "label": "ceiling fan assessment",
        "service": ("/Services/electrical-work", "electrical assessment and licensed-trade routing"),
        "keywords": ["ceiling fan replacement", "wobbly ceiling fan", "fan light repair"],
        "openings": [
            "This {title_lower} gallery is historical project documentation in {place}. Knight Group does not present itself as a licensed electrical contractor. Eligible hang and finish work on an existing box is quoted in writing; new circuits and permit work go to a licensed electrician.",
        ],
        "search": [
            "Ceiling fan replacement and wobbly ceiling fan searches are common after storms and after cheap fans eat their bearings. Balance kits do not fix a box that was never meant to carry a fan.",
        ],
        "methods": [
            ("Confirm the existing box", "A fan-rated box and solid support are the gate. If they are missing, the job routes to licensed electrical."),
            ("Like-for-like hang", "When the written scope allows, swap on the existing support and keep the circuit unchanged."),
            ("Balance and wobble check", "Run the fan through speeds and confirm the light kit if one is in scope."),
            ("Document routing", "Photograph the completed hang and note any licensed follow-up."),
        ],
        "climate": ["Gulf humidity and afternoon storms make a loose canopy a rattle factory. Tighten and document rather than ignoring the noise."],
        "aftercare": ["If the fan starts to wobble again, stop using it and send a photo of the canopy. Do not keep running a loose fixture."],
    },
    "electrical_fixture": {
        "label": "electrical fixture assessment",
        "service": ("/Services/electrical-work", "electrical assessment and licensed-trade routing"),
        "keywords": ["outlet repair", "light fixture replacement", "switch replacement"],
        "openings": [
            "This {title_lower} page in {place} is historical documentation of fixture-level work. Knight Group is not a licensed electrical contractor. Like-for-like device work on an existing box may be quoted; new wiring, panels, and permits are referred.",
        ],
        "search": [
            "Outlet repair and light fixture replacement searches need honest routing language. Homeowners want the device to work; the lawful path is an existing box and a written scope, not a hidden splice.",
        ],
        "methods": [
            ("Inspect the existing box", "Look for damage, overfill, and whether the device is a simple replacement."),
            ("Eligible like-for-like", "Swap the device or fixture only when the written scope and box condition allow."),
            ("Licensed referral", "Stop when the work would be a new circuit, a remodel, or a code correction beyond handyman closeout."),
            ("Test and photograph", "Confirm the device behaves and leave photos for the owner."),
        ],
        "climate": ["Outdoor and garage devices corrode faster near the coast. A tan outlet is often a failed device, not a dirty cover."],
        "aftercare": ["If a breaker trips after the visit, stop using that circuit and call. That is licensed-electrician territory."],
    },
    "floor": {
        "label": "floor and subfloor repair",
        "service": ("/Services/carpentry-framing", "carpentry and framing"),
        "keywords": ["subfloor repair", "soft floor repair", "carpet removal"],
        "openings": [
            "Soft floors in {place} are usually water, pests, or a prior leak that nobody opened. This {title_lower} job cut back to sound material and rebuilt so finish flooring had something to sit on.",
        ],
        "search": [
            "Subfloor repair searches in Florida often follow a bathroom leak or a sliding-glass door that never got a pan. Carpet removal searches are the first half of the same story.",
        ],
        "methods": [
            ("Open the finish", "Remove only the flooring needed to see the damage."),
            ("Cut to sound", "Stop at solid joists or slab and discard delaminated panels."),
            ("Rebuild the deck", "Fasten new material with a gap plan for humidity."),
            ("Prepare for finish", "Leave transitions and height in a state the next floor covering can use."),
        ],
        "climate": ["Slab edge and wet-wall intersections fail first. Photos of stains help quote before the saw comes out."],
        "aftercare": ["Keep the area dry while adhesive or finish cures. Report any bounce that was not there at turnover."],
    },
    "hardware": {
        "label": "hardware and punch-list install",
        "service": ("/Services/general-repairs", "general repairs"),
        "keywords": ["curtain rod install", "grab bar", "TV mount", "fire extinguisher mount"],
        "openings": [
            "Punch-list hardware in {place} fails when someone used drywall anchors in a span that needed a stud. This {title_lower} visit found structure and remounted the hardware so it stays.",
        ],
        "search": [
            "Curtain rod, grab bar, and mount searches are short jobs that still need a stud finder and the right fastener. This gallery is that class of work, not a remodel.",
        ],
        "methods": [
            ("Locate structure", "Find framing or use an appropriate hollow-wall system rated for the load."),
            ("Set fasteners", "Drive hardware level and at the height in the written scope."),
            ("Load test", "Apply a reasonable pull or hang test before leaving."),
            ("Patch leftovers", "Fill abandoned holes from the failed mount when they are in scope."),
        ],
        "climate": ["Concrete block and metal studs are common in Florida. The fastener has to match the wall, not the package photo."],
        "aftercare": ["Do not overload a decorative rod with blackout drapes it was not sized for. Send a photo if a bracket creeps."],
    },
    "general": {
        "label": "handyman repair",
        "service": ("/Services/general-repairs", "general repairs"),
        "keywords": ["handyman near me", "small home repair", "punch list handyman"],
        "openings": [
            "Not every completed job in {place} fits a neat category. This {title_lower} visit was a defined punch-list or repair scope, photographed before and after so the owner has proof of what changed.",
        ],
        "search": [
            "Handyman near me and small home repair remain the umbrella searches that send people to Knight Group. The useful page is still a real job, not a generic service blurb.",
        ],
        "methods": [
            ("Confirm the written scope", "Work only what was agreed, and photograph the starting condition."),
            ("Complete the repair", "Use methods that match the material in front of the technician, not a one-size tutorial."),
            ("Clean and document", "Leave the area broom-clean with after photos on the ticket."),
            ("Note follow-up", "Write down anything that was out of scope or needs a licensed trade."),
        ],
        "climate": ["Tampa Bay houses mix block, frame, and later additions. The first five minutes on site are for figuring out which one you are standing in."],
        "aftercare": ["Keep the before-and-after photos. They help if a related issue shows up next season."],
    },
}

VOICES = (
    "field",
    "homeowner",
    "climate",
    "security",
    "turnover",
    "craft",
)


def _worker_sentence(group: dict, rng: random.Random) -> str:
    name = str(group.get("workerName") or "").strip()
    role = group.get("workerRole") or "field technician"
    month = group.get("completedMonth") or ""
    when = f" in {month}" if month else ""
    if not name:
        options = [
            f"The on-site work was completed by a Knight Group technician{when}.",
            f"A Knight Group field technician ran this visit{when} and is the person in the process photos when those shots exist.",
        ]
        return _pick(rng, options)
    options = [
        f"The on-site work was completed by {name}, {role}{when}.",
        f"{name} ({role}) ran this visit{when} and is the person in the process photos when those shots exist.",
        f"Attribution: {name}, {role}, completed the job{when} for Knight Group Handyman Services.",
    ]
    return _pick(rng, options)


def _photo_sentence(group: dict) -> str:
    before = int(group.get("photoBefore") or 0)
    process = int(group.get("photoProcess") or 0)
    after = int(group.get("photoAfter") or 0)
    bits = []
    if before:
        bits.append(f"{before} before shot{'s' if before != 1 else ''}")
    if process:
        bits.append(f"{process} process shot{'s' if process != 1 else ''}")
    if after:
        bits.append(f"{after} after shot{'s' if after != 1 else ''}")
    if not bits:
        return "The composite on this page is the branded before-and-after record from the completed visit."
    return (
        "The branded composite on this page was built from "
        + ", ".join(bits)
        + " uploaded on the ticket — not stock photography."
    )


def _notes_block(group: dict, worker: str) -> str:
    notes = str(group.get("workNotes") or "").strip()
    if len(notes) < 24:
        return ""
    return (
        f"<h2>How this visit was performed</h2>"
        f"<p>{_esc(worker)} described the completed work in the job record as follows. "
        f"Customer address, phone, and job price are omitted from this public page.</p>"
        f"<blockquote><p>{_esc(notes)}</p></blockquote>"
    )


def _howto(cluster: dict, title: str, licensed: bool) -> str:
    steps = cluster["methods"]
    name = cluster["label"]
    if licensed:
        name = f"How Knight Group documented this {name} visit"
    items = "".join(
        f"<li><strong>{_esc(step)}</strong><p>{_esc(body)}</p></li>" for step, body in steps
    )
    return f'<ol class="kg-howto-steps" data-howto-name="{_esc(name)}">{items}</ol>'


def _keyword_list(cluster: dict, rng: random.Random) -> str:
    words = _take(rng, list(cluster["keywords"]), min(4, len(cluster["keywords"])))
    return ", ".join(f"<strong>{_esc(word)}</strong>" for word in words)


def _sibling_links(group: dict, siblings: list[dict], rng: random.Random) -> list[tuple[str, str]]:
    slug = group.get("id") or ""
    cluster = group.get("cluster")
    same = [
        s
        for s in siblings
        if s.get("id") != slug and s.get("cluster") == cluster and s.get("id")
    ]
    other = [s for s in siblings if s.get("id") != slug and s.get("id")]
    pool = same or other
    rng.shuffle(pool)
    links: list[tuple[str, str]] = []
    for item in pool[:2]:
        label = re.sub(r"\s+—.*$", "", str(item.get("title") or item["id"]))
        links.append((f"/gallery/{item['id']}", label[:70]))
    return links


def _related(
    group: dict,
    cluster: dict,
    siblings: list[dict],
    rng: random.Random,
    licensed: bool,
) -> list[tuple[str, str]]:
    service_href, service_label = cluster["service"]
    if licensed:
        service_href = group.get("serviceLink") or service_href
    city_slug = str(group.get("citySlug") or "")
    county = str(group.get("countyName") or "Pinellas County")
    links: list[tuple[str, str]] = [
        ("/galleries", "All gallery projects"),
        (service_href, service_label),
        (county_href(county), f"{county} handyman"),
    ]
    href = city_href(city_slug)
    city_name = group.get("cityName") or ""
    if href and city_name:
        links.append((href, f"{city_name} handyman"))
    elif city_name == "Lutz":
        links.append(("/tampa-handyman", "Tampa handyman"))
        links.append(("/hillsborough-handyman", "Hillsborough County handyman"))
    links.extend(_sibling_links(group, siblings, rng))
    extras = [
        ("/pricing", "Handyman pricing"),
        ("/booking", "Book a free estimate"),
        ("/handyman-scope-florida", "Handyman scope in Florida"),
        ("/hurricane-repair-handyman-pinellas", "Storm repair notes"),
        ("/about", "About Knight Group"),
        ("/Services/home-repair-near-me", "Home repair near me"),
    ]
    rng.shuffle(extras)
    links.extend(extras[:3])
    # Deduplicate by href, keep order.
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for href, label in links:
        if href in seen:
            continue
        seen.add(href)
        unique.append((href, label))
    return unique[:8]


def _faqs(
    group: dict,
    cluster: dict,
    licensed: bool,
    rng: random.Random,
) -> list[tuple[str, str]]:
    title = str(group.get("title") or cluster["label"]).lower()
    place = place_label(group)
    worker = group.get("workerName") or "a Knight Group technician"
    phone = KG_PHONE
    pool = [
        (
            f"Do you still take {cluster['label']} jobs in {place}?",
            f"Yes, when the written scope stays inside handyman work. Send photos through the booking form or call {phone}. We confirm fit before we schedule.",
        ),
        (
            f"Who completed this {cluster['label']} job?",
            f"{worker} completed the visit documented on this page. Knight Group dispatches by scope and route, so your appointment may be a different technician with the same written process.",
        ),
        (
            "How do I get a price before anyone starts?",
            "Request a free written estimate. Defined small scopes can often be flat-rate; mixed punch lists may be hourly depending on access and materials. Standard published rates are $150 first hour and $75 after, with specialty work at $200 and $100. This gallery page does not publish what this specific job billed.",
        ),
        (
            "Are you registered and insured?",
            "Knight Group Handyman Services LLC is registered and insured in Florida. We perform handyman-scope repairs and refer licensed trades when a permit or specialist is required.",
        ),
        (
            "How soon can you schedule?",
            "Most standard requests schedule within one to two business days. Arrival windows are 8–10, 10–12, or 12–2. Urgent safety issues get priority when you call directly.",
        ),
        (
            "What should I prepare before the visit?",
            "Clear access to the work area, note any prior repairs, and list parts you already purchased. Photos through the booking form help us bring the right tools on the first trip.",
        ),
        (
            f"Why show before-and-after photos for {title}?",
            "Photos prove the starting condition and the closeout. They also help the next homeowner with a similar problem decide whether a handyman-scope visit is the right first call.",
        ),
        (
            "Do you work outside Pinellas County?",
            "Yes, on selected northwest Hillsborough and west Pasco routes when the address fits the day’s board. Lutz and North Tampa are accepted by address confirmation; there is no Lutz office.",
        ),
    ]
    if licensed:
        pool = [
            (
                "Does this historical page mean Knight Group currently offers regulated trade work?",
                "No. Current electrical, plumbing, HVAC, structural, permit-required, pest-control, and regulated mold work is routed to an appropriately licensed or registered provider.",
            ),
            (
                "What can Knight Group quote around a licensed-trade project?",
                "Knight Group can quote eligible documentation, access, cabinet, drywall, caulk, texture, paint, and finish closeout stated in its own written scope.",
            ),
            (
                "How should I request help with a similar condition?",
                f"Send photos of the condition in {place}. We will identify the eligible handyman scope and route the regulated portion before scheduling. Call {phone} for active water or a dead circuit.",
            ),
            pool[2],
            pool[3],
            pool[5],
        ]
    return _take(rng, pool, 5)


def _voice_bridge(voice: str, place: str, label: str) -> str:
    bridges = {
        "field": f"From the truck, {label} in {place} is a sequence: stabilize, correct structure or hardware, then prove the close with photos.",
        "homeowner": f"If you live in {place} and you are searching because the problem is in your way every day, this {label} write-up is meant to read like the visit you actually want, not a brochure.",
        "climate": f"{place} does not have a gentle off-season for building materials. That is why this {label} job is described in Florida terms, not Midwest terms.",
        "security": f"Openings in a fence, a door that will not latch, or a dark fixture are security issues in {place}. This {label} page treats them that way.",
        "turnover": f"Property managers in {place} need a closeout they can show an owner. This {label} composite is that closeout.",
        "craft": f"The craft on a {label} job is in the unglamorous middle: fasteners into real structure, joints that can move with humidity, and a finish that does not telegraph the patch.",
    }
    return bridges.get(voice, bridges["field"])


def _licensed_banner(place: str) -> str:
    return (
        f"<p><strong>Historical project documentation.</strong> Knight Group is a registered and insured "
        f"handyman company serving {place}. This page does not offer licensed electrical, plumbing, HVAC, "
        f"structural, pest-control, or regulated mold contracting. Eligible finish and documentation work "
        f"is quoted separately; regulated portions are routed before we schedule.</p>"
    )


def build_gallery_longform(
    group: dict,
    *,
    siblings: list[dict] | None = None,
    licensed: bool = False,
) -> dict[str, Any]:
    slug = str(group.get("id") or "gallery")
    rng = _seed(slug)
    title = str(group.get("title") or "Handyman project")
    title_lower = re.sub(r"\s+—.*$", "", title).strip().lower()
    cluster_id = infer_cluster(title, str(group.get("cluster") or ""))
    cluster = CLUSTERS.get(cluster_id, CLUSTERS["general"])
    place = place_label(group)
    county = str(group.get("countyName") or "Pinellas County")
    worker = str(group.get("workerName") or "a Knight Group technician")
    role = str(group.get("workerRole") or "field technician")
    month = str(group.get("completedMonth") or "")
    voice = VOICES[rng.randrange(len(VOICES))]
    siblings = siblings or []

    fmt = {
        "place": place,
        "county": county,
        "title_lower": title_lower,
        "worker": worker,
        "role": role,
        "month": month or "a completed visit",
    }

    opening = _pick(rng, cluster["openings"]).format(**fmt)
    search = _pick(rng, cluster["search"]).format(**fmt)
    climate = _pick(rng, cluster["climate"]).format(**fmt) if cluster.get("climate") else ""
    aftercare = _pick(rng, cluster["aftercare"]).format(**fmt) if cluster.get("aftercare") else ""
    extra_search = [s.format(**fmt) for s in cluster["search"] if s.format(**fmt) != search]

    service_href, service_label = cluster["service"]
    city_slug = str(group.get("citySlug") or "")
    city_name = str(group.get("cityName") or "")
    city_link = ""
    if city_href(city_slug) and city_name:
        city_link = (
            f' Local page: <a href="{city_href(city_slug)}">{_esc(city_name)} handyman</a>.'
        )
    elif city_name == "Lutz":
        city_link = (
            ' Lutz work is accepted by address confirmation — there is no Lutz office — and is described '
            'alongside <a href="/tampa-handyman">Tampa handyman</a> routes.'
        )

    sections: list[str] = []
    if licensed:
        sections.append(_licensed_banner(place))
    sections.append(f"<p>{_esc(opening)}</p>")
    sections.append(f"<p>{_esc(_worker_sentence(group, rng))}</p>")
    sections.append(f"<p>{_esc(_photo_sentence(group))}</p>")
    notes_html = _notes_block(group, worker)
    if notes_html:
        sections.append(notes_html)
    sections.append(f"<h2>How the { _esc(cluster['label']) } was handled</h2>")
    sections.append(f"<p>{_esc(_voice_bridge(voice, place, cluster['label']))}</p>")
    sections.append(_howto(cluster, title_lower, licensed))
    sections.append("<h2>What homeowners in this market actually search</h2>")
    sections.append(
        f"<p>{_esc(search)} On this page we highlight {_keyword_list(cluster, rng)} "
        f"because those phrases match the condition in the photos, not because we bought a keyword package.</p>"
    )
    if extra_search:
        sections.append(f"<p>{_esc(_pick(rng, extra_search))}</p>")
    if climate:
        sections.append(f"<h2>Why this fails in { _esc(county) }</h2>")
        sections.append(f"<p>{_esc(climate)}</p>")
    curated = gallery_body_extra(slug)
    if curated and not licensed:
        sections.append(curated)
    sections.append("<h2>Booking a similar visit</h2>")
    sections.append(
        f"<p>Standard published rates remain <strong>$150 first hour / $75 after</strong>, with specialty work at "
        f"<strong>$200 / $100</strong>, and no two-hour minimum on small eligible jobs. This page never lists what "
        f"this specific property paid. Get a free written estimate through "
        f'<a href="/booking">the booking form</a> or call <a href="tel:+18136493341">{KG_PHONE}</a>. '
        f'Read <a href="{service_href}">{_esc(service_label)}</a>, '
        f'<a href="{county_href(county)}">{_esc(county)} coverage</a>, and '
        f'<a href="/pricing">current pricing</a> before you decide.{city_link}</p>'
    )
    if aftercare:
        sections.append(f"<h2>After the crew leaves</h2><p>{_esc(aftercare)}</p>")
    sections.append(
        "<p>Machine-readable site summary for assistants: "
        '<a href="/llms.txt">llms.txt</a> and <a href="/ai.txt">ai.txt</a>. '
        "Google does not rank those files; they exist so crawlers quote the same business facts that humans see.</p>"
    )

    body = "\n".join(sections)
    # Pad with unused climate / search / method commentary until 750 words.
    unused_climate = [c.format(**fmt) for c in cluster.get("climate") or [] if c.format(**fmt) != climate]
    unused_after = [c.format(**fmt) for c in cluster.get("aftercare") or [] if c.format(**fmt) != aftercare]
    pad_i = 0
    pad_pool = unused_climate + unused_after + extra_search
    rng.shuffle(pad_pool)
    while strip_html_words(body) < MIN_WORDS and pad_i < 12:
        if pad_i < len(pad_pool):
            body += f"<p>{_esc(pad_pool[pad_i])}</p>"
        else:
            body += (
                f"<p>Knight Group remains a Safety Harbor company. { _esc(worker) } completed this "
                f"{_esc(cluster['label'])} visit for a {_esc(place)} property, and the composite is the public "
                f"record of that closeout. If your condition looks like the before photos, start with pictures "
                f"and a short description rather than a leftover time window. Arrival windows we quote are "
                f"8–10, 10–12, or 12–2; we do not invent split windows to fill a board.</p>"
            )
            body += (
                f"<p>Internal pages worth reading next include "
                f'<a href="/Services/handyman">handyman services</a>, '
                f'<a href="/service-areas">service areas</a>, and '
                f'<a href="/plumber-background-handyman">Vince’s journeyman plumbing background</a> '
                f"when the question is diagnosis versus a licensed plumber. None of those pages replace the "
                f"photos on this job.</p>"
            )
        pad_i += 1

    body = sanitize_page_text(body)
    related = _related(group, cluster, siblings, rng, licensed)
    faqs = [(q, sanitize_page_text(a)) for q, a in _faqs(group, cluster, licensed, rng)]
    named = worker if worker and not worker.lower().startswith("a knight") else ""
    lead = (
        f"Completed {cluster['label']} in {place}"
        + (f" by {named}" if named else "")
        + ". Before-and-after proof from a real Knight Group visit."
    )
    if licensed:
        lead = f"Historical {cluster['label']} documentation in {place}. Regulated trade work is routed to licensed providers."
    eyebrow = f"{city_name} · {county}" if city_name else county
    return {
        "body_html": body,
        "faqs": faqs,
        "related": related,
        "lead": lead,
        "eyebrow": eyebrow,
        "cluster": cluster_id,
        "word_count": strip_html_words(body),
    }
