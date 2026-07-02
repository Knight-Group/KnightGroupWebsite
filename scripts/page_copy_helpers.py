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
    "emergency-services",
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
            "<strong>Plumbing handyman scope:</strong> Knight Group handles fixture-level repairs and replacements "
            "on existing rough-in — faucets, toilets, disposals, traps, and shutoffs. Repipes, sewer mains, gas lines, "
            "and permitted rough-in require a licensed plumber. We say that before work begins."
        )
    elif slug in ELECTRICAL_SCOPE_SLUGS or "electrical" in slug:
        body = (
            "<strong>Electrical handyman scope:</strong> Knight Group swaps like-for-like fixtures on suitable boxes "
            "and performs minor device repairs within handyman scope. New circuits, panel work, and aluminum wiring "
            "require a licensed electrician — we identify that during the estimate."
        )
    elif slug == "emergency-services":
        body = (
            "<strong>Emergency handyman scope:</strong> Knight Group responds to urgent water, security, and storm "
            "follow-up within handyman limits — stabilizing leaks, securing doors, and triaging damage control. "
            "Licensed emergency plumbers or electricians are referred when code or safety requires it."
        )
    else:
        body = (
            "<strong>Handyman scope notice:</strong> Knight Group performs registered, insured handyman-scope repairs. "
            "Work requiring a licensed plumber, electrician, HVAC contractor, or general contractor permit is identified "
            "before tools come out and referred or coordinated appropriately."
        )
    return f"""
<div class="kg-scope-disclaimer">
  <p>{body}</p>
</div>
"""
