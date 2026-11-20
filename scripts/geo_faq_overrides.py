"""Full FAQ lists for selected geo pages. Used by geo_faq_for_city / geo_faq_for_combo.

These override the five default questions so gallery regenerations keep the
restored visible FAQs (and, with the schema allowlist, the FAQPage node).
Questions and answers are real Knight Group facts already shipped on Oct 31 /
Nov 2 / prepared on Nov 13. No client names or unpublished prices.
"""

from __future__ import annotations

GEO_FAQ: dict[str, list[tuple[str, str]]] = {
    "tampa-handyman": [
        (
            "Do you provide handyman services in Tampa?",
            "Yes. Knight Group serves Tampa as part of our regular Hillsborough County routes from Safety Harbor. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            "Which Tampa neighborhoods do you cover?",
            "We work throughout Tampa including Northwest Tampa, Westchase, Town 'n' Country, Carrollwood, then South Tampa and Hyde Park by confirmation. If you are near the city limits, mention your address when booking so we confirm the route.",
        ),
        (
            "How much does a typical handyman visit cost in Tampa?",
            "Standard visits are $150 for the first hour and $75 each additional hour, with no two-hour minimum. Defined Tampa scopes can be quoted as a flat rate after photos.",
        ),
        (
            "Can Knight Group do plumbing or electrical work in Tampa?",
            "Yes. Ceiling fans, light fixtures, switches, outlets, and basic plumbing (faucets, toilets, sinks, shutoffs) on existing connections are Knight Group work in Tampa. Opening walls, sewer mains, new circuits, and panel work are referred. We are not a licensed plumber or electrician. Hillsborough permit rules can be tighter than Pinellas, so we confirm the county requirement on the written estimate.",
        ),
        (
            "How soon can you reach Tampa?",
            "Most Tampa requests schedule within one to two business days on existing Hillsborough County routes. Active leaks should be called in at (813) 649-3341 so we can triage and involve a licensed plumber when needed.",
        ),
        (
            "Do you give free estimates in Tampa?",
            "Yes, from photos. Send a description and photos and we send a free written quote. We do not do free in-person estimate visits. If the scope changes once we are on site, we revise the quote with you before doing extra work.",
        ),
        (
            "Do you fix ceiling water stains and drywall in Tampa?",
            "Yes. We patch and texture-match ceiling and wall drywall after a leak once the source is fixed, and seal stains with primer before painting. Recent Tampa jobs include a kitchen ceiling patch and a master bath ceiling replaced after a roof vent leak.",
        ),
        (
            "Who will come to my Tampa home?",
            "A Knight Group tech such as Gavin, Sergey, Vince, or Nick. Each completed job is photographed and credited to the tech who did it on our before and after gallery.",
        ),
    ],
    "clearwater-handyman": [
        (
            "Do you provide handyman services in Clearwater?",
            "Yes. Knight Group serves Clearwater as part of our regular Pinellas County routes from Safety Harbor. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            "Which Clearwater neighborhoods do you cover?",
            "We work throughout Clearwater including Island Estates, Coachman Ridge, Countryside, North Clearwater, and Sand Key-adjacent neighborhoods. If you are near the city limits, mention your address when booking so we confirm the route.",
        ),
        (
            "How much does a typical handyman visit cost in Clearwater?",
            "Standard visits are $150 for the first hour and $75 each additional hour, with no two-hour minimum. Defined Clearwater scopes can be quoted as a flat rate after photos.",
        ),
        (
            "Can Knight Group do plumbing or electrical work in Clearwater?",
            "Yes. Ceiling fans, light fixtures, switches, outlets, and basic plumbing (faucets, toilets, sinks, shutoffs) on existing connections are Knight Group work in Clearwater. Opening walls, sewer mains, new circuits, and panel work are referred. We are not a licensed plumber or electrician.",
        ),
        (
            "How soon can you reach Clearwater?",
            "Most Clearwater requests schedule within one to two business days on existing Pinellas County routes. Active leaks should be called in at (813) 649-3341 so we can triage and involve a licensed plumber when needed.",
        ),
        (
            "Do you give free estimates in Clearwater?",
            "Yes, from photos. Send a description and photos and we send a free written quote. We do not do free in-person estimate visits. If the scope changes once we are on site, we revise the quote with you before doing extra work.",
        ),
        (
            "What kinds of jobs do you do in Clearwater?",
            "Mostly repairs and small projects: drywall and texture, ceiling fans, faucets and toilets on existing connections, cabinet and door fixes, flooring patches after leaks, gutter downspout clogs, and punch lists. Recent Clearwater jobs include a kitchen floor repaired after a refrigerator leak and six ceiling fans replaced in one visit.",
        ),
        (
            "Who will come to my Clearwater home?",
            "A Knight Group tech such as Vince, Gavin, Sergey, or Nick. Each completed job is photographed and credited to the tech who did it on our before and after gallery.",
        ),
    ],
    "pinellas-park-handyman": [
        (
            "Do you provide handyman services in Pinellas Park?",
            "Yes. Knight Group serves Pinellas Park as part of our regular Pinellas County routes from Safety Harbor. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            "Which Pinellas Park neighborhoods do you cover?",
            "We work throughout Pinellas Park, including the Park Boulevard, 49th Street, and Ulmerton / Gateway corridors, and nearby addresses toward Largo, Seminole, and St. Petersburg. If you are near the city limits, mention your address when booking so we confirm the route.",
        ),
        (
            "How much does a typical handyman visit cost in Pinellas Park?",
            "Standard visits are $150 for the first hour and $75 each additional hour, with no two-hour minimum. Defined Pinellas Park scopes can be quoted as a flat rate after photos.",
        ),
        (
            "Can Knight Group do plumbing or electrical work in Pinellas Park?",
            "Yes. Ceiling fans, light fixtures, switches, outlets, and basic plumbing (faucets, toilets, sinks, shutoffs) on existing connections are Knight Group work in Pinellas Park. Opening walls, sewer mains, new circuits, and panel work are referred. We are not a licensed plumber or electrician.",
        ),
        (
            "How soon can you reach Pinellas Park?",
            "Most Pinellas Park requests schedule within one to two business days on existing Pinellas County routes. Active leaks should be called in at (813) 649-3341 so we can triage and involve a licensed plumber when needed.",
        ),
        (
            "Do you give free estimates in Pinellas Park?",
            "Yes, from photos. Send a description and photos and we send a free written quote. We do not do free in-person estimate visits. If the scope changes once we are on site, we revise the quote with you before doing extra work.",
        ),
        (
            "What kinds of Pinellas Park jobs have you actually completed?",
            "Recent photographed visits include an exterior gate remount, two drywall cutouts at a sliding door, seven window screens built and installed, a dishwasher replacement, and a bathroom pocket door put back on its track. Each is credited to the tech who did the work in our gallery.",
        ),
        (
            "Who will come to my Pinellas Park home?",
            "A Knight Group tech such as Vince, Gavin, Sergey, or Nick. Each completed job is photographed and credited to the tech who did it on our before and after gallery.",
        ),
    ],
    "largo-handyman": [
        (
            "Do you provide handyman services in Largo?",
            "Yes. Knight Group serves Largo as part of our regular Pinellas County routes from Safety Harbor. Share photos or a short description and we will confirm fit before scheduling.",
        ),
        (
            "Are you a handyman company serving Largo, FL?",
            "Yes. Knight Group Handyman Services LLC is a registered and insured Florida handyman company based in Safety Harbor. We run regular mid-county routes through Largo for repairs, fixtures, and punch-list work. We are not a licensed plumber or electrician.",
        ),
        (
            "Which Largo neighborhoods do you cover?",
            "We work throughout Largo, including Bardmoor, Ridgecrest, Southwest Largo, and the Ulmerton corridor, plus nearby addresses toward Clearwater, Pinellas Park, Seminole, and St. Petersburg. If you are near the city limits, mention your address when booking so we confirm the route.",
        ),
        (
            "Can you handle home repairs in Largo?",
            "Yes. Typical Largo home repairs include drywall and ceiling patches, door and lock fixes, faucet and toilet work on existing connections, tub drain clogs, washer hookups, and yard gate repairs. Send photos so we can confirm the scope. Work that needs a licensed plumber, electrician, or contractor is referred.",
        ),
        (
            "How much does a typical handyman visit cost in Largo?",
            "Standard visits are $150 for the first hour and $75 each additional hour, with no two-hour minimum. Defined Largo scopes can be quoted as a flat rate after photos.",
        ),
        (
            "Do you give free estimates in Largo?",
            "Yes, from photos. Send a description and photos and we send a free written quote. We do not do free in-person estimate visits. If the scope changes once we are on site, we revise the quote with you before doing extra work.",
        ),
        (
            "Do you repair drywall in Largo?",
            "Yes. We patch and paint-ready finish ceiling and wall drywall after a leak or impact, once the source is fixed. A recent Largo visit was a water-stained ceiling that Vince skimmed and painted. Larger water-damage closeout is quoted from photos.",
        ),
        (
            "Can Knight Group do plumbing or electrical work in Largo?",
            "Yes. Ceiling fans, light fixtures, switches, outlets, and basic plumbing (faucets, toilets, sinks, shutoffs) on existing connections are Knight Group work in Largo. Opening walls, sewer mains, new circuits, and panel work are referred. We are not a licensed plumber or electrician.",
        ),
        (
            "How soon can you reach Largo?",
            "Most Largo requests schedule within one to two business days on existing Pinellas County routes. Active leaks should be called in at (813) 649-3341 so we can triage and involve a licensed plumber when needed.",
        ),
    ],
    "tampa-drywall-repair": [
        (
            "Do you offer drywall repair in Tampa?",
            "Yes. Knight Group performs drywall repair in Tampa within handyman scope. Photos help us confirm access, parts, and whether a licensed trade referral is needed.",
        ),
        (
            "How much does drywall repair cost in Tampa?",
            "Pricing depends on access, parts, and finish work. Defined scopes can be flat-rate after photos; complex jobs may be hourly. See our pricing hub or request a written estimate.",
        ),
        (
            "Can you handle drywall or paint after the repair?",
            "Often yes — we sequence drying and finishing so patches do not flash under paint. Mention related rooms when you book.",
        ),
        (
            "Are you licensed and insured?",
            "Knight Group is registered and insured in Florida for handyman-scope work and refers licensed trades when required.",
        ),
        (
            "How do I schedule?",
            "Book online with photos or call (813) 649-3341. Active leaks get priority routing.",
        ),
        (
            "Do you give free estimates for Tampa drywall work?",
            "Yes, from photos. Send a description and photos and we send a free written quote. We do not do free in-person estimate visits. If the scope changes once we are on site, we revise the quote with you before doing extra work.",
        ),
        (
            "What Tampa drywall jobs have you actually completed?",
            "Recent photographed Tampa visits include a kitchen ceiling water-stain patch by Sergey, drywall repair at a pass-through by Kevin, and a master bath ceiling replaced after moisture by Gavin. Each is linked from this page to the before and after gallery.",
        ),
        (
            "Who will do the Tampa drywall work?",
            "A Knight Group tech such as Sergey, Kevin, Gavin, Vince, or Nick. Each completed job is photographed and credited to the tech who did it on our before and after gallery.",
        ),
    ],
}
