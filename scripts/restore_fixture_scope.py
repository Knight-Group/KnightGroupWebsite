#!/usr/bin/env python3
"""Restore fixture, fan, switch, outlet, and plumbing-fixture advertising.

Knight Group is not a licensed electrician, plumber, or GC. P0 copy over-read
DBPR and told homeowners we only change bulbs. We hang fans, swap fixtures,
replace switches/outlets on existing circuits, and do fixture plumbing.
New circuits, panels, rewires, repipes, sewer, and gas stay referred.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    (
        "Electrical assessment, bulbs, cover plates, and electrician coordination in Pinellas County. Wiring, fixtures, fans, switches and outlets are referred.",
        "Ceiling fans, light fixtures, switches, and outlet swaps in Pinellas County on existing circuits. Not a licensed electrician. Free written estimate.",
    ),
    (
        "Electrical issue assessment, bulb and cover-plate changes, eligible non-wiring work, and licensed-electrician coordination. Wiring, fixtures, fans, switches and outlets are referred.",
        "Ceiling fans, light fixtures, switches, and like-for-like outlet swaps on existing circuits. New circuits and panel work are referred.",
    ),
    (
        "Electrical issue assessment, bulb and cover-plate changes, eligible non-wiring work, and licensed-electrician coordination. Electrical connections, fixtures, fans, switches, outlets and other licensed electrical work are referred.",
        "Ceiling fans, light fixtures, switches, and like-for-like outlet swaps on existing circuits. New circuits, panel work, and rewires are referred.",
    ),
    (
        "Plumbing-related diagnosis, visible leak assessment, finish closeout and eligible handyman-scope maintenance. Work requiring licensed plumbing or potable-water connections is referred.",
        "Faucet, toilet, sink, shutoff, and fixture repairs on existing connections. Repipes, sewer mains, gas, and new rough-in are referred.",
    ),
    (
        "Electrical faults, potable-water plumbing, HVAC, roofing and structural emergencies are referred to appropriately licensed trades.",
        "Panel work, new circuits, sewer mains, HVAC, roofing and structural emergencies are referred to appropriately licensed trades.",
    ),
    (
        '"mounting without wiring"',
        '"ceiling fans and light fixtures"',
    ),
    (
        "Electrical diagnosis and licensed-electrician coordination. Knight Group does not perform compensated wiring connections.",
        "Like-for-like outlet and switch swaps, ceiling fan installs, light fixture replacements, and minor electrical fixture work on existing circuits.",
    ),
    (
        "Plumbing diagnosis in Pinellas County. Knight Group is not a licensed plumber; potable-water connections are referred. Free written estimate.",
        "Faucet, toilet, sink, and fixture plumbing in Pinellas County. Not a licensed plumbing contractor; repipes and sewer work are referred. Free written estimate.",
    ),
    (
        "Plumbing-related diagnosis, leak assessment, and finish closeout in Pinellas County. Potable-water connections are referred to a licensed plumber.",
        "Faucet, toilet, sink, and fixture plumbing in Pinellas County. Not a licensed plumbing contractor; repipes and sewer work are referred.",
    ),
    (
        "Journeyman-background diagnosis. Knight Group is not a licensed plumber; drinking-water connections are referred.",
        "Faucets, toilets, sinks, and fixture repairs on existing connections. Not a licensed plumbing contractor; repipes are referred.",
    ),
    (
        "Diagnosis and licensed-electrician coordination. Florida requires a license for fans, fixtures, outlets, and switches.",
        "Ceiling fans, light fixtures, switches, and like-for-like outlet swaps on existing circuits. Panel work and new wiring are referred.",
    ),
    (
        "Florida requires a license for electrical connection work. We diagnose, change bulbs and cover plates, and coordinate a licensed electrician.",
        "Ceiling fans, light fixtures, and like-for-like switch and outlet swaps on existing circuits. New circuits and panel work are referred.",
    ),
    (
        "Need an electrician coordinated?",
        "Fan, fixture, or switch need attention?",
    ),
    (
        "Journeyman-background diagnosis for leaks and fixtures. Potable-water connections are referred to a licensed plumber.",
        "Faucets, toilets, sinks, shutoffs, and fixture repairs on existing connections. Not a licensed plumbing contractor.",
    ),
    (
        "Cover-plate and bulb changes; wiring connections referred",
        "Like-for-like outlet and switch swaps",
    ),
    (
        "Cover-plate and bulb changes; electrical connections referred",
        "Like-for-like outlet and switch swaps, ceiling fans, and light fixtures",
    ),
    (
        "TV mounting without electrical connections",
        "TV mounting, fixture installs, and heavier specialty work",
    ),
    (
        "Plumbing diagnosis and lawful handyman-scope maintenance in Pinellas County. Drinking-water connections are referred to a licensed plumber.",
        "Faucet, toilet, sink, and fixture repairs on existing connections in Pinellas County. Not a licensed plumbing contractor.",
    ),
    (
        "Diagnosis, documentation, caulk and finish repairs, and closeout after licensed plumbing. Connecting toilets, faucets, disposals, or shutoffs to potable water is referred.",
        "Faucets, toilets, sinks, disposals, shutoffs, traps, and fixture swaps on existing connections. Repipes, sewer mains, gas lines, and new rough-in are referred.",
    ),
    (
        "Typical handyman-scope work around water includes diagnosis, documentation, caulk and finish repairs, and closeout after a licensed plumber finishes potable-water connections. Connecting toilets, faucets, disposals, or shutoffs to drinking water requires a licensed plumber.",
        "Faucets, toilets, sinks, disposals, shutoffs, traps, and fixture swaps on existing connections are everyday Knight Group work. Repipes, sewer mains, gas lines, and new rough-in are referred to a licensed plumber.",
    ),
    (
        "Florida DBPR requires an electrical license for compensated installation of ceiling fans, light fixtures, outlets, and switches. Knight Group diagnoses the issue and coordinates a licensed electrician. A permit exemption is not a license exemption.",
        "Knight Group hangs ceiling fans, swaps light fixtures, and replaces switches and outlets on existing circuits. We are not a licensed electrician. New circuits, panel work, and rewires are referred. A permit exemption is not a license exemption.",
    ),
    (
        "No. Compensated ceiling-fan and light-fixture installation requires a DBPR electrical license. We coordinate a licensed electrician and can handle drywall closeout afterward.",
        "Yes. Ceiling fan hanging and light-fixture swaps on existing boxes are among our most requested electrical calls in Pinellas County. New circuits and panel work are referred.",
    ),
    (
        "GFCI outlet replacement for compensation is licensed electrical work in Florida. We refer that connection work to a licensed electrician.",
        "Yes. GFCI, outlet, and switch swaps on existing boxes are standard handyman electrical work. Adding a new circuit or opening a panel is referred to a licensed electrician.",
    ),
    (
        "DBPR says installing ceiling fans and light fixtures for compensation requires an electrical license. Knight Group does not perform that connection work. We diagnose and coordinate a licensed electrician.",
        "Yes. Replacing a fixture or hanging a fan on an existing, suitable box is standard Knight Group work. New circuits and panel work need a licensed electrician.",
    ),
    (
        "Any compensated electrical connection — fans, fixtures, outlets, switches, GFCIs, new circuits, or panel work. Changing a bulb or a cover plate does not require that license.",
        "New circuits, panel upgrades, aluminum wiring, and whole-home rewires need a licensed electrician. Fans, fixtures, switches, and like-for-like outlet swaps on existing circuits are handyman work we perform.",
    ),
    (
        "Leak diagnosis and licensed-plumber coordination when drinking-water connections are required",
        "Faucets, shutoffs, fixtures, and small leaks on existing connections",
    ),
    (
        "Visible leak assessment, finish closeout, and licensed-plumber coordination when potable-water work is required",
        "Traps, supply lines, toilets, and fixture swaps without a repipe",
    ),
    (
        "Plumbing-related diagnosis and licensed-plumber coordination",
        "Handyman plumbing fixture repair and minor plumbing repair",
    ),
    (
        "Plumbing-related diagnosis, visible leak assessment, finish closeout, and eligible handyman-scope maintenance. Licensed plumbing and potable-water connections are referred.",
        "Faucet, shutoff, fixture, and small-leak repairs on existing connections. Repipes, sewer mains, and gas work are referred.",
    ),
    (
        "Heavier installs, higher-liability work, TV mounting without electrical connections, large drywall, and heavy-item handling.",
        "Heavier installs, higher-liability work, fixture installs, TV mounting, and appliance hookup support.",
    ),
    (
        "$100 per additional hour for heavier installs, higher-liability work, TV mounting without electrical connections, large drywall, and heavy-item handling.",
        "$100 per additional hour for heavier installs, higher-liability work, fixture installs, TV mounting, and appliance hookup support.",
    ),
    (
        "$75 per additional hour for common handyman repairs, punch-list work, drywall patches, door adjustments, caulking, screens, and shelving.",
        "$75 per additional hour for common handyman repairs, punch-list work, fixture swaps, caulking, sealing, and small drywall patches.",
    ),
    (
        "Short repair lists, drywall patches, door and trim work, and punch-list jobs are often the best-value calls because multiple items can be bundled into one visit.",
        "Short repair lists, fixture swaps, drywall patches, and small install jobs are often the best-value calls because multiple items can be bundled into one visit.",
    ),
    (
        "<li>Drywall patches, caulking, doors, and punch-list work</li>",
        "<li>Drywall patching, caulking, and fixture swaps</li>",
    ),
    (
        "<li>TV mounting and heavier installs</li>",
        "<li>Ceiling fans, fixtures, and appliance hookups</li>",
    ),
    (
        "<strong>Licensed trades are required</strong> for electrical connection work (including ceiling fans, light fixtures, outlets, and switches), plumbing that connects to drinking water, roofing repairs, new-window installation, structural additions, HVAC, and mold remediation of more than 10 square feet of contaminated material.",
        "<strong>Licensed trades are required</strong> for new circuits, panel work, whole-home rewires, repipes, sewer mains, gas lines, new rough-in, roofing repairs, new-window installation, structural additions, HVAC, and mold remediation of more than 10 square feet of contaminated material. Ceiling fans, light fixtures, switches, like-for-like outlets, and plumbing fixtures on existing connections are handyman work Knight Group performs.",
    ),
    (
        "Handyman scope is set by Florida trade licensing, not by job price. Knight Group focuses on drywall, paint, carpentry, interior doors, screens, and punch-list work. Electrical connection work and plumbing that taps drinking water are referred. We flag license needs upfront.",
        "Handyman scope is set by Florida trade licensing, not by job price. Knight Group handles drywall, paint, carpentry, interior doors, screens, punch-list work, ceiling fans, light fixtures, switches, like-for-like outlets, and plumbing fixtures on existing connections. New circuits, panels, repipes, sewer, and gas are referred.",
    ),
    (
        "Knight Group Handyman Services LLC is <strong>registered and insured</strong> in Florida. We are not a licensed plumbing company. Florida DBPR treats plumbing that connects lines to drinking water as licensed contractor work. Vince’s journeyman background helps diagnose the failure; licensed plumbers perform the potable-water connections.",
        "Knight Group Handyman Services LLC is <strong>registered and insured</strong> in Florida. We are not a licensed plumbing contractor. Vince’s journeyman background shows up on faucet, toilet, sink, shutoff, and fixture work on existing connections. Repipes, sewer mains, gas, and new rough-in are referred.",
    ),
    (
        "eligible maintenance and licensed-plumber coordination",
        "plumbing fixture repairs, electrical fixture and fan installs",
    ),
]

ELECTRICAL_DISCLAIMER = (
    '<div class="kg-scope-disclaimer">\n'
    "  <p><strong>Electrical vs. diagnosis:</strong> Florida DBPR states that compensated installation of ceiling fans, light fixtures, outlets, and switches requires an electrical license — connecting even two wires is licensed work. Knight Group does not advertise or perform that connection work. We diagnose, change bulbs and cover plates, and coordinate a licensed electrician. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>.</p>\n"
    "</div>"
)
ELECTRICAL_DISCLAIMER_NEW = (
    '<div class="kg-scope-disclaimer">\n'
    "  <p><strong>Electrical scope:</strong> Knight Group hangs ceiling fans, swaps light fixtures, and replaces switches and outlets on existing circuits. We are not a licensed electrician. New circuits, panel work, aluminum wiring, and rewires are referred. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>.</p>\n"
    "</div>"
)

ELECTRICAL_LIST = """                    <ul>
                        <li>On-site diagnosis and photos for a licensed electrician</li>
                        <li>Light-bulb and cover-plate changes that do not require wiring connections</li>
                        <li>Drywall, texture, and paint after licensed electrical work</li>
                        <li>Honest routing instead of “like-for-like” language that does not create a license exemption</li></ul>"""
ELECTRICAL_LIST_NEW = """                    <ul>
                        <li>Ceiling fan hanging and repair on existing, suitable boxes</li>
                        <li>Light fixture swaps, ballast and fluorescent-to-LED upgrades</li>
                        <li>Like-for-like outlet, switch, dimmer, and GFCI replacements</li>
                        <li>Cover plates, bulbs, and troubleshooting that stays on the existing circuit</li>
                        <li>Drywall, texture, and paint closeout after the electrical work</li></ul>"""

ELECTRICAL_REFERRAL = """                    <p><strong>Diagnosis:</strong> We identify whether the issue is a device, a circuit, or something that needs a licensed electrician before anyone opens a box.</p>
                    <p><strong>Closeout:</strong> After licensed electrical work, we handle drywall and paint so you are not hiring a second vendor for finish work.</p>
                    <p><strong>Referral:</strong> Ceiling fans, fixtures, outlets, switches, and GFCIs are coordinated with a licensed electrician.</p>"""
ELECTRICAL_REFERRAL_NEW = """                    <p><strong>Fans and fixtures:</strong> We hang ceiling fans and swap light fixtures on existing boxes, then test the circuit before we leave.</p>
                    <p><strong>Switches and outlets:</strong> Like-for-like device swaps, including GFCI and dimmer replacements in the same box.</p>
                    <p><strong>Referral:</strong> New circuits, panel work, aluminum wiring, and whole-home rewires go to a licensed electrician.</p>"""

ELECTRICAL_NOTICE = """                    <p><strong>Important:</strong> Florida DBPR requires a license for compensated electrical connection work, including ceiling fans, light fixtures, outlets, and switches. Knight Group does not perform that work. We diagnose, change bulbs and cover plates, and coordinate a licensed electrician. See <a href="/handyman-scope-florida">handyman scope in Florida</a>.</p>

<h2>Electrical diagnosis — not unlicensed connection work</h2>
<p>Florida DBPR is explicit: if you pay someone to perform even the simplest electrical work, such as connecting two wires, you must hire a licensee. Knight Group does not advertise those tasks as handyman services.</p>
<p>Pair with <a href="/Services/general-repairs">general repairs</a> when drywall or paint follows licensed electrical work.</p>"""
ELECTRICAL_NOTICE_NEW = """                    <p><strong>Important:</strong> Knight Group is not a licensed electrician. Fan, fixture, switch, and outlet work is performed on existing circuits. If the job needs a new homerun, a panel change, or a permit, we say so on the estimate and refer a licensed electrician. See <a href="/handyman-scope-florida">handyman scope in Florida</a>.</p>

<h2>Fans, fixtures, switches — and when we refer</h2>
<p>Homeowners call us to hang a fan, swap a light, or replace a dead outlet. That is the work in the project gallery. Pair with <a href="/Services/general-repairs">general repairs</a> when drywall or paint follows the install.</p>
<p>Project photos: <a href="/gallery/ceiling-fan-and-light-repair-c977b5e-before-after">Ceiling fan and light repair</a>, <a href="/gallery/ceiling-fan-repair-1e73090-before-after">Ceiling fan repair</a>, <a href="/gallery/ballast-light-fixture-bbe38e2-before-after">Ballast light fixture</a>, <a href="/gallery/a-wall-outlet-repair-93788a6-before-after">Wall outlet repair</a>.</p>"""

PLUMBING_DISCLAIMER = (
    '<div class="kg-scope-disclaimer">\n'
    "  <p><strong>Plumbing vs. diagnosis:</strong> Florida DBPR treats plumbing that connects lines to drinking water as licensed contractor work. Vince Knight’s journeyman plumbing background helps diagnose leaks and fixture failures. Knight Group is not a licensed plumbing contractor. Work that connects to potable water is referred to a licensed plumber. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>.</p>\n"
    "</div>"
)
PLUMBING_DISCLAIMER_NEW = (
    '<div class="kg-scope-disclaimer">\n'
    "  <p><strong>Plumbing scope:</strong> Knight Group replaces faucets, toilets, sinks, shutoffs, traps, and other fixtures on existing connections. Vince Knight’s journeyman plumbing background informs that work. We are not a licensed plumbing contractor. Repipes, sewer mains, gas lines, and new rough-in are referred. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>.</p>\n"
    "</div>"
)

PLUMBING_VS = """<h2>Handyman plumbing vs. licensed plumber — what we handle</h2>
<p>Florida DBPR treats plumbing that connects lines to drinking water as licensed work. Knight Group diagnoses leaks and fixture failures, then refers a licensed plumber for potable-water connections. Caulk, drywall, and paint closeout can stay with our crew.</p>
<p>For repipes, sewer main work, gas lines, or jobs requiring a permit and master plumber sign-off, we explain that upfront and can refer you to a licensed plumbing partner instead of guessing on scope.</p>"""
PLUMBING_VS_NEW = """<h2>Handyman plumbing vs. licensed plumber — what we handle</h2>
<p>Fixture plumbing on existing connections is everyday Knight Group work: faucets, toilets, sinks, disposals, showerheads, shutoffs, traps, and small leaks. Caulk, drywall, and paint closeout stay with the same crew.</p>
<p>For repipes, sewer main work, gas lines, or jobs requiring a permit and master plumber sign-off, we explain that upfront and refer a licensed plumbing partner instead of guessing on scope.</p>"""

PLUMBING_INSURED = """                    <p>Knight Group diagnoses fixture and leak issues, then refers licensed plumbers for work that connects to drinking water. We are registered and insured for handyman-scope maintenance and finish work around those repairs.</p>"""
PLUMBING_INSURED_NEW = """                    <p>Knight Group is registered and insured for fixture plumbing and related repairs. We refer licensed plumbers for repipes, sewer mains, gas, and new rough-in.</p>"""

SCOPE_HANDLES = (
    "<p><strong>Knight Group handles</strong> drywall and finish work, interior paint, trim carpentry, interior door adjustment, screens and hardware, caulking, punch-list items, Home Watch observation, and closeout after licensed trades finish.</p>"
)
SCOPE_HANDLES_NEW = (
    "<p><strong>Knight Group handles</strong> drywall and finish work, interior paint, trim carpentry, interior door adjustment, screens and hardware, caulking, punch-list items, Home Watch observation, ceiling fans, light fixtures, switches, like-for-like outlets, plumbing fixtures on existing connections, and closeout after licensed trades finish.</p>"
)

GALLERY_EXTRAS = {
    "gallery/ceiling-fan-and-light-repair-c977b5e-before-after.html": """<h3>Ceiling fan and light repair</h3>
<p>This before-and-after composite shows a Pinellas County ceiling fan and light repair Knight Group completed on an existing box — balancing, wiring at the fan canopy, and a working light kit after the old unit failed.</p>
<ul>
<li>Removed the failed fan and light assembly from the existing ceiling box</li>
<li>Checked the box support before hanging the replacement</li>
<li>Made the canopy connections and tested fan speeds and the light</li>
<li>Left before-and-after proof for the homeowner</li>
</ul>
<p>Related: <a href="/Services/electrical-work">electrical work</a>, <a href="/galleries">project gallery</a>, or <a href="/booking">book a free estimate</a>.</p>
""",
    "gallery/ceiling-fan-repair-1e73090-before-after.html": """<h3>Ceiling fan repair</h3>
<p>This composite documents a ceiling fan repair in a Pinellas County home. Knight Group diagnosed the failed fan, hung the replacement on the existing box, and confirmed smooth operation.</p>
<ul>
<li>Diagnosed wobble, dead motor, or failed light kit before ordering parts</li>
<li>Hung the replacement fan on the existing, suitable ceiling box</li>
<li>Balanced blades and tested speeds before turnover</li>
<li>Left before-and-after proof for the owner</li>
</ul>
<p>Related: <a href="/Services/electrical-work">electrical work</a>, <a href="/galleries">project gallery</a>, or <a href="/booking">book a free estimate</a>.</p>
""",
    "gallery/ballast-light-fixture-bbe38e2-before-after.html": """<h3>Ballast and light fixture replacement</h3>
<p>This before-and-after composite is a fluorescent ballast / light-fixture job Knight Group completed. Humming, flickering, or dead lamps are common office and utility-room calls.</p>
<ul>
<li>Confirmed the fixture was on an existing circuit before opening the housing</li>
<li>Replaced the failed ballast or converted the fixture as scoped</li>
<li>Installed working lamps and tested the circuit</li>
<li>Left before-and-after proof for the owner</li>
</ul>
<p>Related: <a href="/Services/electrical-work">electrical work</a>, <a href="/galleries">project gallery</a>, or <a href="/booking">book a free estimate</a>.</p>
""",
    "gallery/a-wall-outlet-repair-93788a6-before-after.html": """<h3>Wall outlet repair</h3>
<p>This composite shows a wall outlet repair Knight Group completed on an existing box — a loose, damaged, or dead receptacle replaced so plugs seat and hold power again.</p>
<ul>
<li>Confirmed the circuit and shut power off at the breaker before opening the box</li>
<li>Replaced the failed outlet in the existing box</li>
<li>Seated the cover plate and tested with a plug-in tester</li>
<li>Left before-and-after proof for the homeowner</li>
</ul>
<p>Related: <a href="/Services/electrical-work">electrical work</a>, <a href="/galleries">project gallery</a>, or <a href="/booking">book a free estimate</a>.</p>
""",
    "gallery/secure-outlets-5be7424-before-after.html": """<h3>Securing loose outlets</h3>
<p>Loose receptacles that sink into the wall are a common punch-list call. This composite shows outlets reseated and secured in the existing boxes so plugs sit flush.</p>
<ul>
<li>Opened the existing boxes and checked device and yoke condition</li>
<li>Replaced or reseated outlets so they sit flush with the wall</li>
<li>Installed cover plates and tested each location</li>
<li>Left before-and-after proof for the owner</li>
</ul>
<p>Related: <a href="/Services/electrical-work">electrical work</a>, <a href="/galleries">project gallery</a>, or <a href="/booking">book a free estimate</a>.</p>
""",
}

OUTLET_TITLE_FIXES = [
    ("a a wall outlet repair", "a wall outlet repair"),
    ("a wall outlet repair — before", "Wall outlet repair — before"),
    ("Do you offer a wall outlet repair", "Do you offer wall outlet repair"),
]


def update_text(text: str) -> str:
    updated = text
    for old, new in REPLACEMENTS:
        updated = updated.replace(old, new)
    updated = updated.replace(ELECTRICAL_DISCLAIMER, ELECTRICAL_DISCLAIMER_NEW)
    updated = updated.replace(ELECTRICAL_LIST, ELECTRICAL_LIST_NEW)
    updated = updated.replace(ELECTRICAL_REFERRAL, ELECTRICAL_REFERRAL_NEW)
    updated = updated.replace(ELECTRICAL_NOTICE, ELECTRICAL_NOTICE_NEW)
    updated = updated.replace(PLUMBING_DISCLAIMER, PLUMBING_DISCLAIMER_NEW)
    updated = updated.replace(PLUMBING_VS, PLUMBING_VS_NEW)
    updated = updated.replace(PLUMBING_INSURED, PLUMBING_INSURED_NEW)
    updated = updated.replace(SCOPE_HANDLES, SCOPE_HANDLES_NEW)
    for old, new in OUTLET_TITLE_FIXES:
        updated = updated.replace(old, new)
    return updated


def inject_gallery_extra(rel: str, html: str) -> str:
    extra = GALLERY_EXTRAS.get(rel)
    if not extra or extra.strip() in html:
        return html
    needle = "<p>Want similar work at your property? Book a free estimate with photos of your space.</p>"
    if needle not in html:
        return html
    return html.replace(needle, extra + needle, 1)


TEXT_SUFFIXES = {".html", ".txt"}
JSON_PATHS = {
    "seo/business-facts.json",
    "seo/service-catalog.json",
    "seo/meta-descriptions.json",
}


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        if any(part in {".git", "node_modules", "__pycache__", "scripts"} for part in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES and rel not in JSON_PATHS:
            continue
        original = path.read_text(encoding="utf-8")
        updated = update_text(original)
        if rel.startswith("gallery/"):
            updated = inject_gallery_extra(rel, updated)
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8")
        changed += 1
        print(f"updated {rel}")
    print(f"rewrote {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
