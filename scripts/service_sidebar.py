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


def render_service_sidebar(
    slug: str,
    label: str,
    lead: str | None = None,
    county_name: str = "Pinellas County",
) -> str:
    token = _slug_token(slug)
    book_label = label.strip().rstrip(".")
    sidebar_lead = lead or (
        f"Send the basics and we will follow up with clear pricing for your {county_name} project."
    )
    subject = f"Knight Group {book_label} Estimate Request"

    return f"""                        <aside class="kg-service-sidebar" aria-labelledby="{token}-sidebar-heading">
                            <div class="kg-pricing-sidebar-form">
                                <h3 class="kg-sidebar-title" id="{token}-sidebar-heading">Book {html.escape(book_label.lower())}</h3>
                                <p>{html.escape(sidebar_lead)}</p>
                                <form class="kg-contact-form" action="https://formspree.io/f/xzzvnpne" method="POST" data-kg-guard>
                                    <div class="kg-field">
                                        <label for="{token}-sidebar-name">Your name</label>
                                        <input type="text" id="{token}-sidebar-name" name="name" autocomplete="name" placeholder="First and last name" required>
                                    </div>
                                    <div class="kg-field">
                                        <label for="{token}-sidebar-phone">Phone</label>
                                        <input type="tel" id="{token}-sidebar-phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="(813) 555-1234" required>
                                    </div>
                                    <div class="kg-field kg-field--optional">
                                        <label for="{token}-sidebar-message">Project details <span>(optional)</span></label>
                                        <textarea id="{token}-sidebar-message" name="message" rows="3" placeholder="Job type, city, or timing"></textarea>
                                    </div>
                                    <input type="hidden" name="_subject" value="{html.escape(subject)}">
                                    <input type="hidden" name="request_type" value="{html.escape(book_label)}">
                                    <input type="hidden" name="service_page" value="{html.escape(slug)}">
                                    <input type="hidden" name="_next" value="https://www.knightgroup.com/thank-you">
                                    <label class="visually-hidden" for="{token}-sidebar-hp">Leave this field blank</label>
                                    <input class="kg-hp" id="{token}-sidebar-hp" type="text" name="address_2" autocomplete="off" tabindex="-1">
                                    <button type="submit" class="kg-contact-form__submit" data-kg-sending="Sending">Get free estimate</button>
                                </form>
                            </div>

                            <div class="pricing-highlights">
                                <h3>Why homeowners choose Knight Group</h3>
                                <ul>
                                    <li>No 2-hour minimums</li>
                                    <li>Transparent, upfront pricing</li>
                                    <li>Registered and insured</li>
                                    <li>Free written estimates</li>
                                    <li>Local Safety Harbor business</li>
                                    <li>5.0 Google rating</li>
                                    <li>Journeyman plumbing background</li>
                                    <li>{html.escape(county_name)} coverage</li>
                                </ul>
                            </div>

                            <h3>Quick contact</h3>
                            <div class="pricing-highlights">
{PHONE_CTA}
                                <p style="margin-top:16px;"><strong>Email:</strong> <a href="mailto:nknight@knightgroup.com">nknight@knightgroup.com</a></p>
                                <p><strong>Hours:</strong> Mon&ndash;Fri 8 AM&ndash;5 PM<br>Weekends and after hours: emergency calls only</p>
                                <p style="margin-top:16px;"><a href="/booking">Prefer the full booking form?</a></p>
                            </div>
                        </aside>"""
