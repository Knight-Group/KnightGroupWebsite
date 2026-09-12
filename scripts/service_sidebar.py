#!/usr/bin/env python3
"""Shared sticky service-page sidebar matching pricing-page design."""

from __future__ import annotations

import html
import re

PHONE_CTA = """
                        <a href="tel:+18136493341" class="header-btn-primary kg-header-call" title="Click to call or text (813) 649-3341" aria-label="Call or text (813) 649-3341">
                            <span class="kg-header-call__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" width="18" height="18" focusable="false"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.3 21 3 13.7 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
                            </span>
                            <span class="kg-header-call__text">
                                <span class="kg-header-call__label">Call or Text</span>
                                <span class="kg-header-call__number">(813) 649-3341</span>
                            </span>
                        </a>"""


def _slug_token(slug: str) -> str:
    token = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    return token or "service"


def render_photo_fields(field_id: str) -> str:
    """Photos required, or a promise to text them to Voice."""
    return f"""                                    <div class="kg-field kg-photo-field">
                                        <label for="{field_id}-photos">Job photos</label>
                                        <input type="file" id="{field_id}-photos" name="photos" accept="image/*" multiple>
                                        <p class="kg-field-hint">A close-up and a wide shot are enough for most written quotes.</p>
                                        <label class="kg-check">
                                            <input type="checkbox" name="text_photos" id="{field_id}-text-photos" value="I will text photos to (813) 649-3341">
                                            <span>I will text photos to (813) 649-3341</span>
                                        </label>
                                        <p class="kg-photo-error" hidden>Add photos here, or check that you will text them to (813) 649-3341.</p>
                                    </div>
"""


def render_service_sidebar(
    slug: str,
    label: str,
    lead: str | None = None,
    county_name: str = "Pinellas County",
) -> str:
    token = _slug_token(slug)
    book_label = label.strip().rstrip(".")
    sidebar_lead = lead or (
        f"Photos first — most {county_name} jobs are quoted in writing within 24 business hours."
    )
    subject = f"Knight Group {book_label} Estimate Request"
    form_title = f"Book {html.escape(book_label.lower())}"
    submit_label = "Get a written estimate"
    packet_html = ""
    is_pm = slug == "property-manager-handyman"
    extra_fields = ""
    message_placeholder = "Job type, city, or timing"
    name_placeholder = "First and last name"
    if is_pm:
        extra_fields = f"""                                    <div class="kg-field">
                                        <label for="{token}-sidebar-company">Management company</label>
                                        <input type="text" id="{token}-sidebar-company" name="company" autocomplete="organization" placeholder="Legal name for the COI" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="{token}-sidebar-email">Email</label>
                                        <input type="email" id="{token}-sidebar-email" name="email" autocomplete="email" placeholder="Work email" required>
                                    </div>
"""
        message_placeholder = "Property address, work-order #, or certificate-holder name"
        name_placeholder = "Your name at the management company"
        highlights_title = "Why property managers add Knight Group"
        highlight_lines = [
            "Downloadable W-9 and GL COI",
            "Photo-documented work orders",
            "$150 first hour / $75 after",
            "No 2-hour minimum",
            "Officer WC exemptions on file",
            "Not a licensed plumber or GC",
            "10+ years Florida property management",
            "Pinellas first — selected Hillsborough/Pasco",
        ]
        form_title = "Add Knight Group as a vendor"
        submit_label = "Send vendor request"
        packet_html = (
            f'                                <p><a class="kg-btn kg-btn--solid" href="/vendor/knight-group-vendor-packet.zip" '
            f'download>Download vendor packet (ZIP)</a></p>\n'
        )
    else:
        highlights_title = "Why homeowners choose Knight Group"
        highlight_lines = [
            "No 2-hour minimums",
            "Transparent, upfront pricing",
            "Registered and insured",
            "Free written estimates",
            "Local Safety Harbor business",
            "5.0 Google rating",
            "+15 Years as Journeyman Plumber",
            "+20 Years Property Management",
            f"{county_name} coverage",
        ]
    highlights_items = "\n                                    ".join(
        f"<li>{html.escape(item)}</li>" for item in highlight_lines
    )

    return f"""                        <aside class="kg-service-sidebar" aria-labelledby="{token}-sidebar-heading">
                            <div class="kg-pricing-sidebar-form">
                                <h3 class="kg-sidebar-title" id="{token}-sidebar-heading">{form_title}</h3>
                                <p>{html.escape(sidebar_lead)}</p>
{packet_html}                                <form class="kg-contact-form" action="https://formspree.io/f/xzzvnpne" method="POST" data-kg-guard>
                                    <div class="kg-field">
                                        <label for="{token}-sidebar-name">Your name</label>
                                        <input type="text" id="{token}-sidebar-name" name="name" autocomplete="name" placeholder="{html.escape(name_placeholder)}" required>
                                    </div>
{extra_fields}                                    <div class="kg-field">
                                        <label for="{token}-sidebar-phone">Phone</label>
                                        <input type="tel" id="{token}-sidebar-phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="(813) 555-1234" required>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="{token}-sidebar-message">Project details <span>(optional)</span></label>
                                        <textarea id="{token}-sidebar-message" name="message" rows="3" placeholder="{html.escape(message_placeholder)}"></textarea>
                                    </div>
{render_photo_fields(token + "-sidebar")}                                    <input type="hidden" name="_subject" value="{html.escape(subject)}">
                                    <input type="hidden" name="request_type" value="{html.escape(book_label)}">
                                    <input type="hidden" name="service_page" value="{html.escape(slug)}">
                                    <input type="hidden" name="_next" value="https://www.knightgroup.com/thank-you">
                                    <label class="visually-hidden" for="{token}-sidebar-hp">Leave this field blank</label>
                                    <input class="kg-hp" id="{token}-sidebar-hp" type="text" name="address_2" autocomplete="off" tabindex="-1">
                                    <button type="submit" class="kg-contact-form__submit" data-kg-sending="Sending">{html.escape(submit_label)}</button>
                                </form>
                            </div>

                            <div class="pricing-highlights">
                                <h3>{html.escape(highlights_title)}</h3>
                                <ul>
                                    {highlights_items}
                                </ul>
                            </div>

                            <h3>Quick contact</h3>
                            <div class="pricing-highlights">
{PHONE_CTA}
                                <p style="margin-top:16px;"><strong>Email:</strong> <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a></p>
                                <p><strong>Hours:</strong> Mon&ndash;Fri 8 AM&ndash;5 PM<br>After-hours callback when available; no guaranteed response time</p>
                                <p style="margin-top:16px;"><a href="/booking">Prefer the full booking form?</a></p>
                            </div>
                        </aside>"""
