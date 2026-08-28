"""HTML-side PII sweep for generated gallery pages.

Mirrors Dispatch sanitizer rules so a leaked address or dollar amount cannot
ship in page HTML even if catalog facts were incomplete.
"""
from __future__ import annotations

import re

KG_PHONE_DISPLAY = "(813) 649-3341"

_PRIVATE_TERMS_RE = re.compile(
    r"\b(?:copeland(?:\s+morgan)?(?:\s+llc)?|vendoroo|managebuilding|"
    r"work\s*order)\b",
    re.I,
)
_STREET_RE = re.compile(
    r"\b\d{1,6}\s+(?:[NSEW]\.?\s+)?(?:[A-Za-z0-9.'-]+\s+){0,7}"
    r"(?:street|st|avenue|ave|drive|dr|road|rd|lane|ln|boulevard|blvd|"
    r"court|ct|way|place|pl|terrace|ter|circle|cir)\b[^,;]*",
    re.I,
)
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
_MONEY_RE = re.compile(r"\$\s*\d[\d,]*(?:\.\d{2})?")
_TICKET_RE = re.compile(
    r"\b(?:KG|PM|KL|ST|FW)-?\d{8}-?[A-Z0-9]{3,}\b|\b(?:WO|ticket)\s*#?\s*[A-Z0-9-]{5,}\b",
    re.I,
)
_ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")

# Published retail rates are allowed in generated copy. Job-specific amounts
# from tickets are not. After stripping $ amounts, restore these phrases.
_ALLOWED_RATES = (
    "$150 first hour / $75 after",
    "$200 / $100",
    "$150 first hour and $75 after",
    "$200 and $100",
)


def strip_html_words(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"&[a-z]+;", " ", text, flags=re.I)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def sanitize_page_text(html: str, *, extra_needles: list[str] | None = None) -> str:
    text = html or ""
    placeholders: dict[str, str] = {}
    for index, phrase in enumerate(_ALLOWED_RATES):
        token = f"KGRATE{index}"
        if phrase.lower() in text.lower():
            # case-preserving replace via regex
            text = re.sub(re.escape(phrase), token, text, flags=re.I)
            placeholders[token] = phrase
    text = text.replace(KG_PHONE_DISPLAY, "KGPHONE")
    text = text.replace("813-649-3341", "KGPHONE")
    text = text.replace("tel:+18136493341", "KGTEL")
    for needle in extra_needles or []:
        raw = str(needle or "").strip()
        if len(raw) >= 8 and "@" not in raw:
            # Do not strip job notes; only obvious identifiers.
            continue
    text = _EMAIL_RE.sub(" ", text)
    text = _PHONE_RE.sub(" ", text)
    text = _STREET_RE.sub(" ", text)
    text = _TICKET_RE.sub(" ", text)
    text = _MONEY_RE.sub(" ", text)
    text = _ZIP_RE.sub(" ", text)
    text = _PRIVATE_TERMS_RE.sub(" ", text)
    text = text.replace("KGPHONE", KG_PHONE_DISPLAY)
    text = text.replace("KGTEL", "tel:+18136493341")
    for token, phrase in placeholders.items():
        text = text.replace(token, phrase)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text
