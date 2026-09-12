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
                "Knight Group Handyman Services LLC is <strong>registered and insured</strong> in Florida. We are not a licensed plumbing contractor. Vince’s journeyman background shows up on faucet, toilet, sink, shutoff, and fixture work on existing connections. Opening walls, sewer mains, gas, and new rough-in are referred.",
                "That honesty matters in Pinellas County homes: older shutoffs, mixed DIY history, and Florida humidity create jobs that look simple until someone opens the wall. Experience helps you get a straight answer before drywall is torn out or the wrong part is ordered.",
                "See <a href=\"/Services/plumbing-services\">plumbing services</a>, read <a href=\"/handyman-scope-florida\">what handyman scope includes in Florida</a>, or <a href=\"/booking\">get a free written estimate</a> with photos of the problem area.",
            ]
        )
    if slug == "rental-turnover-handyman":
        return prose_block(
            [
                defn["lead"],
                "Vince Knight managed Florida rental properties for roughly <strong>ten years</strong> before Knight Group — useful when you need move-in ready work on a deadline, not a homeowner-paced hobby project. One registered team can knock out mixed punch lists instead of coordinating four separate trades for small items.",
                "Typical turnover scopes include door and hardware adjustments, drywall patches and touch-up paint, caulk refresh, blind and screen repairs, garbage disposal replacement, minor flooring transitions, and the “tenant broke it” items that stack up between leases.",
                "We work with individual landlords and small property managers across Safety Harbor, Clearwater, Dunedin, Palm Harbor, Largo, and nearby Pinellas communities. Share a unit address, photos, and your target ready date — we return a written estimate and confirm what fits handyman scope versus licensed trade work.",
                "Pricing can be hourly for mixed lists or flat-rate for defined scopes. There is <a href=\"/pricing-no-2-hour-minimum\">no 2-hour minimum</a> on small jobs. See <a href=\"/Services/general-repairs\">general repairs</a> and <a href=\"/Services/painting-finishing\">painting &amp; finishing</a>, or <a href=\"/contact\">contact us</a> for multi-unit schedules.",
                "To add <strong>Knight Group Handyman Services LLC</strong> as a recurring vendor — W-9, GL certificate, work-order photos — use the <a href=\"/property-manager-handyman\">property manager vendor page</a>. This page stays the vacant-unit punch list.",
            ]
        )
    if slug == "handyman-scope-florida":
        return prose_block(
            [
                defn["lead"],
                "Florida homeowners search “licensed handyman” constantly — but handyman businesses are typically <strong>registered and insured</strong>, not licensed plumbers, electricians, or general contractors. Knight Group is transparent about that distinction. Public claims on this site follow current <a href=\"https://www2.myfloridalicense.com/services-requiring-a-dbpr-license/\">DBPR consumer guidance</a>.",
                "<strong>Knight Group handles</strong> drywall and finish work, interior paint, trim carpentry, interior door adjustment, screens and hardware, caulking, punch-list items, Home Watch observation, ceiling fans, light fixtures, switches, like-for-like outlets, plumbing fixtures on existing connections, and closeout after licensed trades finish.",
                "<strong>Licensed trades are required</strong> for new circuits, panel work, whole-home rewires, repipes, sewer mains, gas lines, new rough-in, roofing repairs, new-window installation, structural additions, HVAC, and mold remediation of more than 10 square feet of contaminated material. Ceiling fans, light fixtures, switches, like-for-like outlets, and plumbing fixtures on existing connections are handyman work Knight Group performs.",
                "<strong>Pinellas permit note:</strong> effective July 1, 2026, some projects under $7,500 can qualify for limited permit exemptions only with Building Official approval. A permit exemption is not a contractor-license exemption.",
                "<strong>Hillsborough note:</strong> Fixture and fan work is quoted the same way when the job does not need a permit. Hillsborough permit rules can be tighter than Pinellas, so we confirm the county requirement on the written estimate.",
                "Owner Vince Knight’s journeyman plumbing <em>experience</em> helps on diagnosis and honest routing; it does not replace a plumbing license. Read <a href=\"/plumber-background-handyman\">why that experience still matters</a>.",
            ]
        )
    if slug == "hurricane-repair-handyman-pinellas":
        return prose_block(
            [
                defn["lead"],
                "Pinellas County sits on the Gulf — every June through November, homeowners balance <strong>hurricane prep</strong> with the reality that tropical storms still cause leaks, blown screens, and drywall damage even when the house “survives.” Knight Group is a registered and insured handyman team based in Safety Harbor, not a licensed general contractor or restoration franchise.",
                "<strong>Before storm season</strong>, we help with practical prep inside handyman scope: refreshing exterior caulk at doors and windows, checking door sweeps and weatherstripping, tightening loose soffit panels where accessible, rescreening porch panels, and clearing small maintenance items that fail under wind-driven rain.",
                "<strong>After a storm</strong>, call <a href=\"tel:+18136493341\">(813) 649-3341</a> if water is still moving — see <a href=\"/Services/emergency-services\">emergency services</a>. Once leaks are stopped, we handle drywall patches, texture and paint touch-ups, door and hardware adjustments, and documented punch lists for landlords and insurers. We are not adjusters, but written scopes help your claim packet.",
                "Knight Group does not perform structural engineering, major tree removal, or permitted re-roofing. We coordinate honestly when a licensed roofer, plumber, or electrician is required. Compare <a href=\"/Services/water-damage-repair\">water damage repair</a>, <a href=\"/Services/general-repairs\">general repairs</a>, and <a href=\"/pinellas-handyman\">Pinellas County coverage</a>, or <a href=\"/booking\">book a prep walkthrough</a> with photos.",
            ]
        )
    if slug == "property-manager-handyman":
        return _property_manager_vendor_prose()
    return prose_block([defn["lead"]])


def _property_manager_vendor_prose() -> str:
    """Vendor-hire packet for PMs. Keep unique; do not repeat the hero lead."""
    return """
<h2>Add Knight Group as your Pinellas handyman vendor</h2>
<p>This page is the vendor file for <strong>Knight Group Handyman Services LLC</strong> — the company property managers, landlords, HOA boards, and small commercial desks add when they need a registered, insured handyman on work orders. It is not a homeowner “handyman near me” landing page, and it is not a second brand. You add this LLC. Overflow help is dispatched as Knight Group, not as a roster of other companies on this website.</p>
<p>Property managers searching <em>commercial handyman near me</em> or <em>property maintenance handyman</em> are usually looking for a vendor packet: legal name, FEIN, certificate of insurance, photo standards, and a written number — not another city page written for homeowners.</p>

<h3>Vendor packet — copy these fields, or download the PDFs</h3>
<p>Use the same legal entity on AppFolio, Buildium, RentVine, Property Meld, or a paper vendor folder. The zip below is the packet we already send when a property manager adds Knight Group Handyman Services LLC: filled W-9 (EIN, not a Social Security number), GL certificate, both managers’ Florida workers’ compensation officer exemptions, Sunbiz LLC proof, and the services one-pager.</p>
<p class="kg-vendor-download">
    <a class="kg-btn kg-btn--solid" href="/vendor/knight-group-vendor-packet.zip" download>Download vendor packet (ZIP)</a>
</p>
<ul>
<li><a href="/vendor/knight-group-w9.pdf">Filled IRS W-9</a> (Knight Group Handyman Services LLC, EIN 33-2557284)</li>
<li><a href="/vendor/knight-group-gl-certificate.pdf">ACORD 25 general liability</a> ($1M / $2M; certificate holder is proof of coverage)</li>
<li><a href="/vendor/knight-group-wc-exemption-nicholas-knight.pdf">Florida WC officer exemption — Nicholas J. Knight</a></li>
<li><a href="/vendor/knight-group-wc-exemption-vincent-knight.pdf">Florida WC officer exemption — Vincent E. Knight</a></li>
<li><a href="/vendor/knight-group-sunbiz-llc.pdf">Sunbiz LLC annual report</a> (L24000528363)</li>
<li><a href="/vendor/knight-group-services-one-pager.pdf">Services one-pager</a></li>
</ul>
<ul>
<li><strong>Legal name:</strong> Knight Group Handyman Services LLC</li>
<li><strong>DBA:</strong> Knight Group</li>
<li><strong>FEIN:</strong> 33-2557284</li>
<li><strong>Florida LLC (Sunbiz document):</strong> L24000528363</li>
<li><strong>Managers:</strong> Nicholas J. Knight and Vincent E. Knight</li>
<li><strong>Vendor contact:</strong> Nicholas Knight · <a href="tel:+18136493341">(813) 649-3341</a> · <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a></li>
<li><strong>Remit and physical address:</strong> 1225 7th St S, Safety Harbor, FL 34695</li>
<li><strong>Hours:</strong> Monday–Friday 8:00 a.m.–5:00 p.m. After-hours callback when someone is available; this is not a 24/7 dispatch desk.</li>
</ul>
<p>The downloadable COI is proof of coverage. If your vendor file needs your management company as additional insured, email the exact legal name and we reissue. ACH and bank details are not in the zip — email <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a> after you approve the vendor.</p>

<h3>Insurance we can attach today</h3>
<p>Knight Group carries commercial general liability at <strong>$1 million per occurrence / $2 million aggregate</strong>. That certificate is what most Pinellas and Tampa Bay property managers ask for on day one. We are registered and insured as a handyman company. We are <strong>not</strong> a licensed plumber, electrician, HVAC contractor, roofer, or general contractor, and we will not sign your vendor form as if we were. Scope rules are on <a href="/handyman-scope-florida">handyman scope in Florida</a>.</p>
<p>Both managers hold Florida Division of Workers’ Compensation <strong>officer exemptions</strong>. The LLC does not currently have a company workers’ compensation policy, so the workers’ compensation block on the general-liability certificate is blank. Some management companies approve vendors on GL plus officer exemptions. Others will not. We will not tell your file that a company WC certificate exists until one is bound and in your inbox. If a bound company WC policy is a hard gate, say so in the first email.</p>

<h2>How property-maintenance work orders run</h2>
<p>Send the work order the way your desk already works: email, the form on this page, <a href="/booking">the booking form</a>, or a photo text to (813) 649-3341. We do not require you to change software. If you use AppFolio, Buildium, or another vendor portal, invite <strong>Knight Group Handyman Services LLC</strong> and we will upload completion photos and invoices there. We do not sell a native API integration and we do not need you to log into ours.</p>
<p>Typical cycle on a business day: acknowledge the ticket, confirm what is handyman-scope versus a licensed trade, return a written estimate, schedule an arrival window, complete the work, and send before-and-after photos with a unit-level invoice. Standard arrival windows are <strong>8–10, 10–12, and 12–2</strong>. We do not quote split windows such as 10:30–12:30. A 2–4 window is a first-hour exception when commute time is on the clock — ask before you promise an owner that slot.</p>
<p>Active water, an unsecured opening, or storm damage: call. Everything else can wait for a close-up and a wide shot. Lockbox codes, gate codes, and pet notes belong on the work order. Occupied units need a resident contact; vacant make-ready needs the ready date and whether paint is included.</p>
<p>Photo standard on closeout: one wide shot of the room or elevation, one close-up of the finished repair, and the work-order or unit number in the filename or the email subject. Invoices use the property address and unit, a short description a bookkeeper can bill an owner without calling us, and materials listed separately from labor. If your portal needs a specific cost-code, put it on the ticket before we start.</p>

<div class="kg-contact-methods" aria-label="How property managers send work orders">
    <div class="kg-contact-method">
        <span class="kg-contact-method__icon" aria-hidden="true">WO</span>
        <div>
            <h3>Work orders</h3>
            <p>Email, portal invite, or photos. We reply with a written number before tools come out.</p>
        </div>
    </div>
    <div class="kg-contact-method">
        <span class="kg-contact-method__icon" aria-hidden="true">COI</span>
        <div>
            <h3>Vendor PDFs</h3>
            <p><a href="/vendor/knight-group-vendor-packet.zip" download>Download the ZIP</a> — W-9, GL certificate, both WC exemptions, Sunbiz, one-pager.</p>
        </div>
    </div>
    <div class="kg-contact-method">
        <span class="kg-contact-method__icon" aria-hidden="true">$</span>
        <div>
            <h3>$150 first hour</h3>
            <p>$75 each hour after on standard handyman work. No two-hour minimum. Specialty $200/$100.</p>
        </div>
    </div>
</div>

<h2>Property maintenance a commercial handyman actually finishes</h2>
<p>Most vendor tickets are not a remodel. They are drywall, paint, doors, hardware, screens, caulk, trim, blinds, and closeout after a licensed plumber or electrician leaves. Vince Knight managed Florida rental property for about <strong>ten years</strong> before Knight Group, which is why estimates read like a manager’s file — unit, issue, photos, ready date — instead of a homeowner punch list that grows in the driveway.</p>
<ul>
<li>Occupied work orders and make-ready lists that fit handyman scope</li>
<li>Common-area doors, hardware, drywall, and paint (not elevators, fire systems, or roofing)</li>
<li>Photo documentation you can forward to an owner without rewriting our notes</li>
<li>Vacant-unit turnovers — the dedicated page is <a href="/rental-turnover-handyman">rental turnover handyman</a></li>
<li>Pinellas vacant-house walkthroughs on <a href="/home-watch-pinellas">Home Watch</a> (observation and photos, not a repair ticket)</li>
<li>Small commercial suites and offices when the work is the same handyman scope as a rental</li>
</ul>
<p>Related finish work: <a href="/Services/general-repairs">general repairs</a>, <a href="/Services/drywall-repair">drywall repair</a>, <a href="/Services/painting-finishing">painting and finishing</a>, <a href="/Services/doors-windows">doors and windows</a>. Fixture plumbing and fan installs: <a href="/plumber-background-handyman">journeyman plumbing background</a> and <a href="/Services/plumbing-services">plumbing services</a>.</p>

<h2>What this vendor will not sign</h2>
<p>In-wall plumbing, sewer mains, panel or new-circuit work, permitted additions, structural repairs, HVAC, and mold remediation over ten square feet are referred. Hillsborough permit rules can be tighter than Pinellas — we confirm on the estimate. We will tell you that instead of hoping the work order closes.</p>
<p>Knight Group Handyman Services LLC is the only vendor this site asks you to add. Other businesses are not advertised here, are not a second Google Business Profile, and are not a substitute legal name on your COI.</p>

<h2>Where property-manager routes actually run</h2>
<p>Pinellas County is the home board: Safety Harbor, Clearwater, Dunedin, Palm Harbor, Largo, Oldsmar, Tarpon Springs, Seminole, and St. Petersburg. Selected northwest Hillsborough and west Pasco tickets are accepted when the day’s route already exists — not as a promise that every Tampa ZIP is a same-day commercial handyman call. Recurring Home Watch stays Pinellas-focused. Confirm the address before you tell an owner we are “the Tampa vendor.” See <a href="/service-areas">service areas</a> and <a href="/pinellas-handyman">Pinellas coverage</a>.</p>

<h2>Published pricing on vendor work orders</h2>
<p>Public retail matches <a href="/pricing">published pricing</a>: <strong>$150 first hour / $75 each additional hour</strong> on standard handyman work, <strong>$200 / $100</strong> on specialty, with <a href="/pricing-no-2-hour-minimum">no two-hour minimum</a>. Mixed work orders are often hourly. A defined make-ready list can be a written flat rate after photos or a walkthrough. Private network or platform rates are not published on this site. Net terms and ACH instructions belong on your vendor file and the invoice — never in a public HTML table.</p>

<h2>Vacant unit versus the vendor relationship</h2>
<p>One empty apartment and a Friday ready date belongs on <a href="/rental-turnover-handyman">rental turnover</a>. Snowbirds and empty houses that need a walkthrough, not a punch list, belong on <a href="/home-watch-pinellas">Home Watch</a>. This page is the approved-vendor relationship: repeating work orders, COI, W-9, and photo standards under <strong>Knight Group Handyman Services LLC</strong>.</p>
<p>Email the questionnaire to <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a>, call <a href="tel:+18136493341">(813) 649-3341</a>, or use the form. Put the certificate-holder legal name in the first message so the ACORD 25 does not have to be reissued.</p>
"""


def trust_faqs(slug: str) -> list[tuple[str, str]]:
    if slug == "plumber-background-handyman":
        return [
            (
                "Is Knight Group a licensed plumbing company?",
                "No. Knight Group Handyman Services LLC is a registered and insured handyman business. Vince Knight has journeyman plumbing experience from his prior career, which informs fixture-level repairs — not a current plumbing contractor license.",
            ),
            (
                "What plumbing work can an experienced handyman handle?",
                "Typical handyman-scope work around water includes faucets, toilets, sinks, disposals, shutoffs, traps, and small leaks on existing connections. Opening walls, sewer mains, gas lines, and new rough-in need a licensed plumber.",
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
                "Yes — punch lists and unit turns are on this page. To add Knight Group Handyman Services LLC as a vendor (W-9, certificate of insurance, repeating work orders), use the property manager handyman page.",
            ),
            (
                "What is usually included in a rental turnover punch list?",
                "Common items include drywall patches, paint touch-ups, door hardware, caulk, blinds and screens, and minor floor or trim fixes — bundled into one visit when possible.",
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
                "What registration and insurance does Knight Group carry?",
                "Knight Group is registered and insured in Florida as a handyman services company. We are not licensed as a plumber, electrician, or general contractor — we are clear about that and refer licensed trades when required.",
            ),
            (
                "What work does Knight Group quote as handyman scope?",
                "Knight Group quotes drywall, paint, carpentry, interior doors, screens, hardware, caulking, punch-list work, ceiling fans, light fixtures, switches, outlets, and basic plumbing that does not need a permit. New circuits, panel work, in-wall plumbing, and sewer work are referred. We are not a licensed electrician, plumber, or general contractor.",
            ),
            (
                "When should I hire a licensed plumber instead of a handyman?",
                "Opening walls, sewer mains, gas lines, new rough-in, and permit-sign-off jobs need a licensed plumber. Fixture plumbing on existing connections — faucets, toilets, sinks, disposals, shutoffs — is Knight Group work. We quote eligible finish work around a referred job.",
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
                "Yes — after the moisture source is stopped, cavities are dry, and any required licensed mold remediation is complete, we patch drywall, retexture, and paint. Florida licenses mold remediation above 10 square feet. We do not advertise mold remediation as a Knight Group service.",
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
    if slug == "property-manager-handyman":
        return [
            (
                "Where do I download the W-9 and insurance?",
                "Download the vendor packet ZIP from this page. It includes the filled IRS W-9 (EIN 33-2557284), the ACORD 25 GL certificate, both managers’ Florida workers’ compensation officer exemptions, Sunbiz LLC proof, and the services one-pager. ACH is not in the zip. Email nknight@knightgroup.com if you need your company named as additional insured.",
            ),
            (
                "Do you carry workers’ compensation?",
                "Both managers have Florida officer exemptions. The LLC does not currently have a company workers’ compensation policy, so that block on the GL certificate is blank. We will not claim a company WC certificate until one is bound. Ask if exemptions plus GL are enough for your vendor committee.",
            ),
            (
                "Do you take commercial handyman work orders and property maintenance tickets?",
                "Yes. Email, portal invite, or photos. We return a written estimate, schedule 8–10, 10–12, or 12–2, and send completion photos. We are not a licensed plumber, electrician, or general contractor.",
            ),
            (
                "What does a property manager pay?",
                "Published retail is $150 first hour and $75 each hour after on standard handyman work, $200 / $100 on specialty, with no two-hour minimum. Mixed work orders are often hourly; defined make-ready lists can be flat-rate after photos. Private vendor-network rates are not listed on this site.",
            ),
            (
                "Is this the same page as rental turnover?",
                "No. Rental turnover is the vacant-unit punch list. This page is the vendor relationship: W-9, COI, repeating work orders, and photo standards for Knight Group Handyman Services LLC.",
            ),
        ]
    return []


def trust_related_links(slug: str) -> list[tuple[str, str]]:
    common = [
        ("/about", "About Knight Group"),
        ("/booking", "Get a free written estimate"),
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
            ("/property-manager-handyman", "Property manager vendor packet"),
            ("/Services/general-repairs", "General repairs"),
            ("/Services/painting-finishing", "Painting & finishing"),
            ("/pricing-no-2-hour-minimum", "No 2-hour minimum"),
            *common,
        ]
    if slug == "property-manager-handyman":
        return [
            ("/rental-turnover-handyman", "Rental turnover punch lists"),
            ("/handyman-scope-florida", "Handyman scope in Florida"),
            ("/home-watch-pinellas", "Home Watch for vacant houses"),
            ("/pricing-no-2-hour-minimum", "No 2-hour minimum"),
            ("/Services/general-repairs", "General repairs"),
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
