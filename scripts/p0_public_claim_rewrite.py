#!/usr/bin/env python3
"""One-shot public-claim cleanup: licensed-trade language and leaked SEO copy."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    (
        "Mold remediation (minor to moderate)",
        "Drywall and finish restoration after the moisture source is addressed",
    ),
    (
        "Minor roof and gutter repairs",
        "Gutter repairs; roofing is referred to a licensed roofer",
    ),
    (
        "Custom pergolas and gazebos",
        "Outdoor benches and planters that are not structural additions",
    ),
    (
        "Outdoor structures and pergolas",
        "Repair carpentry that is not a structural addition",
    ),
    (
        "Storm window installation",
        "Screen and hardware repairs",
    ),
    (
        "Yes. We install pre-hung exterior doors, security doors, screen doors, and sliding glass doors throughout Pinellas County. We ensure proper weather sealing and alignment.",
        "We adjust interior doors, hardware, and screens. New exterior-door and window installation is licensed construction in Florida and is referred.",
    ),
    (
        "24/7 Emergency Handyman Services in Pinellas County, FL",
        "Urgent Property-Damage Response in Pinellas County, FL",
    ),
    (
        "24/7 Emergency Handyman in Pinellas County FL | Knight Group",
        "Urgent Handyman Response in Pinellas County FL | Knight Group",
    ),
    (
        "24/7 Emergency Handyman Services",
        "Urgent Property-Damage Response",
    ),
    (
        "24/7 emergency handyman",
        "urgent handyman response",
    ),
    (
        "Available 24/7",
        "After-hours callback",
    ),
    (
        "available 24/7",
        "available for after-hours callback",
    ),
    (
        "24/7 urgent repairs when you need them most. Available evenings, weekends, and holidays.",
        "Call (813) 649-3341 for active water, unsecured openings, or storm follow-up. Posted hours are Monday–Friday 8 AM–5 PM, with after-hours callback — not a 24/7 dispatch desk.",
    ),
    (
        "Knight Group is available 24/7 to handle the crisis.",
        "Knight Group takes urgent calls and will tell you whether we can stabilize the scene or a licensed trade should go first.",
    ),
    (
        "We provide 24/7 emergency services throughout Pinellas County",
        "We provide urgent response throughout Pinellas County during posted hours and after-hours callback",
    ),
    (
        "See our <a href=\"/Services/emergency-services\">24/7 emergency handyman services</a>",
        "See our <a href=\"/Services/emergency-services\">urgent property-damage response</a>",
    ),
    (
        "Florida handymen can perform minor electrical tasks such as replacing outlets, switches, light fixtures, ceiling fans, and doorbell wiring without a permit in most cases. Work requiring a permit is coordinated with a licensed electrician.",
        "Knight Group hangs ceiling fans, swaps light fixtures, and replaces switches and outlets on existing circuits. We are not a licensed electrician — new circuits, panel work, and rewires are referred. A permit exemption is not a license exemption.",
    ),
    (
        "Florida DBPR requires an electrical license for compensated installation of ceiling fans, light fixtures, outlets, and switches. Knight Group diagnoses the issue and coordinates a licensed electrician. A permit exemption is not a license exemption.",
        "Knight Group hangs ceiling fans, swaps light fixtures, and replaces switches and outlets on existing circuits. We are not a licensed electrician. New circuits, panel work, and rewires are referred. A permit exemption is not a license exemption.",
    ),
    (
        "Yes — ceiling fan installation and light fixture swaps are two of our most requested electrical services throughout Pinellas County and Safety Harbor.",
        "Yes. Ceiling fan hanging and light-fixture swaps on existing boxes are among our most requested electrical calls in Pinellas County. New circuits and panel work are referred.",
    ),
    (
        "No. Compensated ceiling-fan and light-fixture installation requires a DBPR electrical license. We coordinate a licensed electrician and can handle drywall closeout afterward.",
        "Yes. Ceiling fan hanging and light-fixture swaps on existing boxes are among our most requested electrical calls in Pinellas County. New circuits and panel work are referred.",
    ),
    (
        "Yes. GFCI outlet replacement is a standard service we perform in kitchens, bathrooms, and outdoor areas throughout Pinellas County.",
        "Yes. GFCI, outlet, and switch swaps on existing boxes are standard handyman electrical work. Adding a new circuit or opening a panel is referred to a licensed electrician.",
    ),
    (
        "GFCI outlet replacement for compensation is licensed electrical work in Florida. We refer that connection work to a licensed electrician.",
        "Yes. GFCI, outlet, and switch swaps on existing boxes are standard handyman electrical work. Adding a new circuit or opening a panel is referred to a licensed electrician.",
    ),
    (
        "Like-for-like outlet and switch swaps, ceiling fan installs, light fixture replacements, and minor electrical fixture work within handyman scope.",
        "Like-for-like outlet and switch swaps, ceiling fan installs, light fixture replacements, and minor electrical fixture work on existing circuits.",
    ),
    (
        "Electrical diagnosis and licensed-electrician coordination. Knight Group does not perform compensated wiring connections.",
        "Like-for-like outlet and switch swaps, ceiling fan installs, light fixture replacements, and minor electrical fixture work on existing circuits.",
    ),
    (
        "Handyman electrical work in Pinellas County: ceiling fans, fixtures, switches, and like-for-like replacements on existing circuits. Free written estimate.",
        "Ceiling fans, light fixtures, switches, and outlet swaps in Pinellas County on existing circuits. Not a licensed electrician. Free written estimate.",
    ),
    (
        "Electrical diagnosis in Pinellas County. Florida requires a license for fans, fixtures, outlets, and switches. Free written estimate.",
        "Ceiling fans, light fixtures, switches, and outlet swaps in Pinellas County on existing circuits. Not a licensed electrician. Free written estimate.",
    ),
    (
        "Core local positioning instead of broad, vague service-area copy.",
        "Locally owned shop at 1225 7th St S — not a distant franchise dispatch desk.",
    ),
    (
        "These are the pages we want Google and homeowners to treat as the primary answers for common local handyman searches.",
        "Start with the service that matches the job. Each page explains what Knight Group handles and when a licensed trade is the right call.",
    ),
    (
        "Cover-plate and bulb changes; wiring connections referred",
        "Like-for-like outlet and switch swaps",
    ),
    (
        "45-minute outlet install: about $150 total",
        "A typical first-hour visit: $150, then $75/hour",
    ),
]


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if any(part in {"node_modules", ".git", "GalleryImages"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in REPLACEMENTS:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated {path.relative_to(ROOT)}")
    print(f"rewrote {changed} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
