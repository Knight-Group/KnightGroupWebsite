"""Prose and FAQ copy for trust / guide landing pages."""

from __future__ import annotations


def prose_block(paragraphs: list[str]) -> str:
    return "".join(f"<p>{p}</p>\n" for p in paragraphs)


def build_trust_prose(defn: dict) -> str:
    slug = defn["slug"]
    if slug == "plumber-background-handyman":
        return prose_block(
            [
                defn["lead"],
                "Most handyman ads say “we do plumbing.” Few can explain whether your leak is a failed gasket, a corroded shutoff, or the start of a repipe. Vince Knight spent <strong>15 years as a journeyman plumber</strong> before launching Knight Group — that trade background shapes how we diagnose fixture-level work, not a license claim.",
                "Knight Group Handyman Services LLC is <strong>registered and insured</strong> in Florida. We are not a licensed plumbing company today. We handle handyman-scope fixture repairs — faucets, toilets, disposals, drains, shutoffs, and minor leak corrections on existing connections — and we tell you plainly when a licensed plumber or permit is required.",
                "That honesty matters in Pinellas County homes: older shutoffs, mixed DIY history, and Florida humidity create jobs that look simple until someone opens the wall. Experience helps you get a straight answer before drywall is torn out or the wrong part is ordered.",
                "See <a href=\"/Services/plumbing-services\">plumbing services</a>, read <a href=\"/handyman-scope-florida\">what handyman scope includes in Florida</a>, or <a href=\"/booking\">book a free estimate</a> with photos of the problem area.",
            ]
        )
    if slug == "rental-turnover-handyman":
        return prose_block(
            [
                defn["lead"],
                "Vince Knight managed Florida rental properties for roughly <strong>ten years</strong> before Knight Group — useful when you need move-in ready work on a deadline, not a homeowner-paced hobby project. One registered team can knock out mixed punch lists instead of coordinating four separate trades for small items.",
                "Typical turnover scopes include door and hardware adjustments, drywall patches and touch-up paint, fixture swaps, caulk refresh, blind and screen repairs, garbage disposal replacement, minor flooring transitions, and the “tenant broke it” items that stack up between leases.",
                "We work with individual landlords and small property managers across Safety Harbor, Clearwater, Dunedin, Palm Harbor, Largo, and nearby Pinellas communities. Share a unit address, photos, and your target ready date — we return a written estimate and confirm what fits handyman scope versus licensed trade work.",
                "Pricing can be hourly for mixed lists or flat-rate for defined scopes. There is <a href=\"/pricing-no-2-hour-minimum\">no 2-hour minimum</a> on small jobs. See <a href=\"/Services/general-repairs\">general repairs</a> and <a href=\"/Services/painting-finishing\">painting &amp; finishing</a>, or <a href=\"/contact\">contact us</a> for multi-unit schedules.",
            ]
        )
    if slug == "handyman-scope-florida":
        return prose_block(
            [
                defn["lead"],
                "Florida homeowners search “licensed handyman” constantly — but handyman businesses are typically <strong>registered and insured</strong>, not licensed plumbers, electricians, or general contractors. Knight Group is transparent about that distinction so you know what we can do in-house and when we refer a licensed trade.",
                "<strong>Knight Group handles</strong> handyman-scope repairs: drywall patches, interior paint touch-ups, carpentry and trim, door and window adjustments, fixture-level plumbing on existing rough-in, like-for-like electrical fixture swaps on suitable boxes, caulking, punch-list items, and smaller renovation support.",
                "<strong>Licensed trades are required</strong> for work such as repipes, sewer mains, gas lines, new electrical circuits, panel upgrades, structural engineering projects, and jobs that need a permit sign-off. We explain that during the estimate — we do not bluff through scope to win the call.",
                "Owner Vince Knight’s journeyman plumbing <em>experience</em> helps on diagnosis and honest routing; it does not replace a master plumber license when Florida law or your insurer requires one. Read <a href=\"/plumber-background-handyman\">why that experience still matters</a> or <a href=\"/Services/plumbing-services\">plumbing services we perform</a>.",
            ]
        )
    if slug == "hurricane-repair-handyman-pinellas":
        return prose_block(
            [
                defn["lead"],
                "Pinellas County sits on the Gulf — every June through November, homeowners balance <strong>hurricane prep</strong> with the reality that tropical storms still cause leaks, blown screens, and drywall damage even when the house “survives.” Knight Group is a registered and insured handyman team based in Safety Harbor, not a licensed general contractor or restoration franchise.",
                "<strong>Before storm season</strong>, we help with practical prep inside handyman scope: refreshing exterior caulk at doors and windows, checking door sweeps and weatherstripping, tightening loose soffit panels where accessible, rescreening porch panels, and clearing small maintenance items that fail under wind-driven rain.",
                "<strong>After a storm</strong>, call <a href=\"tel:+18136493341\">(813) 649-3341</a> if water is still moving — see <a href=\"/Services/emergency-services\">emergency services</a>. Once leaks are stopped, we handle drywall patches, texture and paint touch-ups, door and hardware adjustments, fixture swaps, and documented punch lists for landlords and insurers. We are not adjusters, but written scopes help your claim packet.",
                "Knight Group does not perform structural engineering, major tree removal, or permitted re-roofing. We coordinate honestly when a licensed roofer, plumber, or electrician is required. Compare <a href=\"/Services/water-damage-repair\">water damage repair</a>, <a href=\"/Services/general-repairs\">general repairs</a>, and <a href=\"/pinellas-handyman\">Pinellas County coverage</a>, or <a href=\"/booking\">book a prep walkthrough</a> with photos.",
            ]
        )
    return prose_block([defn["lead"]])


def trust_faqs(slug: str) -> list[tuple[str, str]]:
    if slug == "plumber-background-handyman":
        return [
            (
                "Is Knight Group a licensed plumbing company?",
                "No. Knight Group Handyman Services LLC is a registered and insured handyman business. Vince Knight has journeyman plumbing experience from his prior career, which informs fixture-level repairs — not a current plumbing contractor license.",
            ),
            (
                "What plumbing work can an experienced handyman handle?",
                "Typical handyman-scope plumbing includes faucet and toilet repairs, garbage disposal swaps, drain clearing, shutoff replacement, and minor leak corrections on existing connections. Repipes, gas work, and permitted rough-in require a licensed plumber.",
            ),
            (
                "Why does journeyman experience matter if you are not licensed now?",
                "It speeds honest diagnosis — you hear sooner whether a job is a gasket, a valve, or a reason to call a licensed plumber, which saves time and bad tear-outs on Pinellas County homes.",
            ),
            (
                "Do you serve Clearwater and Safety Harbor for plumbing handyman work?",
                "Yes — Knight Group is based in Safety Harbor and serves Pinellas County communities including Clearwater, Dunedin, Palm Harbor, and Largo.",
            ),
        ]
    if slug == "rental-turnover-handyman":
        return [
            (
                "Do you work with property managers in Pinellas County?",
                "Yes — we take punch-list and turnover work for landlords and small property managers. Share photos and a ready date for a written estimate.",
            ),
            (
                "What is usually included in a rental turnover punch list?",
                "Common items include drywall patches, paint touch-ups, door hardware, fixture swaps, caulk, blinds and screens, disposal replacement, and minor floor or trim fixes — bundled into one visit when possible.",
            ),
            (
                "Can you bill hourly for mixed turnover tasks?",
                "Yes — mixed punch lists are often hourly from $75–$150 depending on work type, with no 2-hour minimum. Defined scopes can be flat-rate after photos or a walkthrough.",
            ),
            (
                "Are you licensed general contractors?",
                "No — we operate as registered and insured handyman services. Larger renovation or permit-heavy work is scoped separately or referred when a GC or licensed trade is required.",
            ),
        ]
    if slug == "handyman-scope-florida":
        return [
            (
                "Is Knight Group licensed and insured?",
                "Knight Group is registered and insured in Florida as a handyman services company. We are not licensed as a plumber, electrician, or general contractor — we are clear about that and refer licensed trades when required.",
            ),
            (
                "What can a handyman legally do in Florida?",
                "Handyman scope varies by job type and local rules. Knight Group focuses on repairs and improvements that do not require a specialist license — fixture swaps, drywall, paint, carpentry, doors, and punch-list work — and we flag permit or license needs upfront.",
            ),
            (
                "When should I hire a licensed plumber instead of a handyman?",
                "Repipes, sewer work, gas lines, new rough-in, and permit-sign-off jobs need a licensed plumber. Many everyday fixture repairs on existing connections fit handyman scope — we assess and explain before work starts.",
            ),
            (
                "Does experience replace a license?",
                "No. Experience helps with diagnosis and honest scope; it does not replace a license when Florida law or your insurance requires one. Knight Group refers out rather than overpromising.",
            ),
        ]
    if slug == "hurricane-repair-handyman-pinellas":
        return [
            (
                "Does Knight Group board up windows for hurricanes?",
                "We help with handyman-scope prep such as caulk refresh, weatherstripping, screen repair, and securing loose trim where accessible. Full structural boarding or permitted storm shutters may need a licensed contractor — we assess and explain during the estimate.",
            ),
            (
                "Can you repair drywall after hurricane water damage?",
                "Yes — after active leaks are stopped and cavities are dry, we patch drywall, retexture, and paint within handyman scope. Extensive mold remediation or structural drying may require specialists first.",
            ),
            (
                "Do you offer emergency handyman service after a storm?",
                "Call (813) 649-3341 for urgent water or security issues. We clarify same-day availability and whether you need a licensed emergency plumber instead of handyman-scope work.",
            ),
            (
                "Which Pinellas cities do you serve for storm repairs?",
                "Knight Group routes daily from Safety Harbor through Clearwater, Dunedin, Palm Harbor, Largo, Oldsmar, Seminole, and nearby Pinellas communities.",
            ),
        ]
    return []


def trust_related_links(slug: str) -> list[tuple[str, str]]:
    common = [
        ("/about", "About Knight Group"),
        ("/booking", "Book a free estimate"),
        ("/Services/handyman", "Handyman services"),
    ]
    if slug == "plumber-background-handyman":
        return [
            ("/Services/plumbing-services", "Plumbing services"),
            ("/handyman-scope-florida", "Handyman scope in Florida"),
            *common,
        ]
    if slug == "rental-turnover-handyman":
        return [
            ("/Services/general-repairs", "General repairs"),
            ("/Services/painting-finishing", "Painting & finishing"),
            ("/pricing-no-2-hour-minimum", "No 2-hour minimum"),
            *common,
        ]
    if slug == "hurricane-repair-handyman-pinellas":
        return [
            ("/Services/emergency-services", "Emergency services"),
            ("/Services/water-damage-repair", "Water damage repair"),
            ("/Services/general-repairs", "General repairs"),
            *common,
        ]
    return [
        ("/plumber-background-handyman", "Journeyman plumbing experience"),
        ("/Services/plumbing-services", "Plumbing services"),
        *common,
    ]
