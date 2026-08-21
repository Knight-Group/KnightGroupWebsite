"""Unique FAQ intros, CTA copy, and trade-specific scope disclaimers for service pages."""

from __future__ import annotations

import hashlib
import re

FAQ_INTRO_TEMPLATES = (
    "Questions homeowners in {county} ask before booking {topic}.",
    "What to know about {topic} in {county} before you schedule.",
    "Straight answers about {topic} from a registered Safety Harbor handyman team serving {county}.",
    "Common {topic} questions across Safety Harbor, Clearwater, and {county}.",
    "Planning {topic}? Start with these homeowner questions we hear in {county}.",
    "Scope, pricing, and scheduling questions for {topic} in {county}.",
    "Before we roll a truck for {topic}, homeowners in {county} usually ask:",
    "Local {topic} FAQ — written for {county} homeowners, not a national template.",
)

CTA_LEAD_TEMPLATES = (
    "Share photos, your city, and a short description of the {topic} work — we reply with a written estimate before scheduling.",
    "Tell us the address, access notes, and what you want handled for {topic}. We confirm scope and pricing before tools come out.",
    "Describe the {topic} issue and upload pictures through our booking form or call (813) 649-3341 for urgent water or security concerns.",
    "List rooms affected and your target date for {topic}. Mixed punch lists are welcome — we quote the full scope upfront.",
    "Send dimensions, photos, and any parts you already purchased for {topic}. We confirm handyman scope versus licensed trade needs first.",
    "Note whether the property is owner-occupied or a rental turnover — it helps us plan {topic} visits across {county}.",
    "For {topic}, include close-ups and a wide shot of the work area. We follow up with a free written estimate during business hours.",
    "Call for active leaks; otherwise book online with photos for {topic} in {county}. We confirm fit and pricing before work starts.",
)

PLUMBING_SCOPE_SLUGS = {
    "plumbing-services",
    "faucet-replacement",
    "sink-faucet-repair",
    "toilet-repair",
    "garbage-disposal-replacement",
    "shutoff-valve-repair",
    "drain-unclogging",
}

ELECTRICAL_SCOPE_SLUGS = {"electrical-work"}


def _topic_label(h1: str, slug: str) -> str:
    text = (h1 or slug.replace("-", " ")).strip().rstrip(".")
    if text.isupper():
        return text.lower()
    return text[0].lower() + text[1:] if text else slug.replace("-", " ")


def _slot(slug: str, modulo: int) -> int:
    digest = hashlib.sha256(slug.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulo


def faq_intro(slug: str, h1: str, county_name: str = "Pinellas County") -> str:
    topic = _topic_label(h1, slug)
    template = FAQ_INTRO_TEMPLATES[_slot(slug, len(FAQ_INTRO_TEMPLATES))]
    return template.format(topic=topic, county=county_name)


def cta_lead(slug: str, h1: str, county_name: str = "Pinellas County") -> str:
    topic = _topic_label(h1, slug)
    template = CTA_LEAD_TEMPLATES[_slot(f"{slug}-cta", len(CTA_LEAD_TEMPLATES))]
    return template.format(topic=topic, county=county_name)


def scope_disclaimer_html(slug: str) -> str:
    if slug in PLUMBING_SCOPE_SLUGS or any(token in slug for token in ("plumb", "faucet", "toilet", "drain", "disposal", "shutoff", "sink")):
        body = (
            "<strong>Plumbing vs. diagnosis:</strong> Florida DBPR treats plumbing that connects lines to drinking water "
            "as licensed contractor work. Vince Knight’s journeyman plumbing background helps diagnose leaks and "
            "fixture failures. Knight Group is not a licensed plumbing contractor. Work that connects to potable water "
            "is referred to a licensed plumber. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>."
        )
    elif slug in ELECTRICAL_SCOPE_SLUGS or "electrical" in slug:
        body = (
            "<strong>Electrical vs. diagnosis:</strong> Florida DBPR states that compensated installation of ceiling fans, "
            "light fixtures, outlets, and switches requires an electrical license — connecting even two wires is licensed "
            "work. Knight Group does not advertise or perform that connection work. We diagnose, change bulbs and cover "
            "plates, and coordinate a licensed electrician. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>."
        )
    elif slug == "emergency-services":
        body = (
            "<strong>Urgent property-damage response:</strong> Call (813) 649-3341 for active water, unsecured openings, "
            "or storm follow-up. Knight Group can stabilize what is lawful and safe (documentation, drying setup, "
            "hardware, temporary protection) during posted hours and after-hours callback. Electrical faults, potable "
            "plumbing repairs, HVAC, roofing, and structural damage go to licensed trades. This is not a 24/7 dispatch "
            "operation. See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>."
        )
    else:
        body = (
            "<strong>Handyman scope notice:</strong> Knight Group is registered and insured for handyman-scope repairs. "
            "Florida licenses electrical connection work, plumbing that taps drinking water, roofing, new-window "
            "installation, structural additions, and mold remediation over 10 square feet. We identify that during the "
            "estimate and refer licensed trades. A Pinellas permit exemption is not a contractor-license exemption. "
            "See <a href=\"/handyman-scope-florida\">handyman scope in Florida</a>."
        )
    return f"""
<div class="kg-scope-disclaimer">
  <p>{body}</p>
</div>
"""
