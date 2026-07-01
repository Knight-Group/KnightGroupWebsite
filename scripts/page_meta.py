"""Resolve meta descriptions and Open Graph / Twitter tags for generated pages."""

from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "seo" / "meta-descriptions.json"
MAX_LEN = 159
MIN_LEN = 120

OG_IMAGE = "https://www.knightgroup.com/Images/knightgroup-og-card-1200x630-clean.png"
TWITTER_IMAGE = "https://www.knightgroup.com/Images/knightgroup-twitter-card-1200x628-phone.png"


def clip_title(title: str, max_len: int = 60) -> str:
    text = " ".join(title.split())
    if len(text) <= max_len:
        return text
    for needle in (" FL", " Services", " County"):
        candidate = text.replace(needle, "", 1)
        if len(candidate) <= max_len:
            return candidate
    if "|" in text:
        parts = [part.strip() for part in text.split("|")]
        compact = f"{parts[0]} | Knight Group"
        if len(compact) <= max_len:
            return compact
    return text[: max_len - 3].rstrip() + "..."


def esc(value: str) -> str:
    return html.escape(value.strip(), quote=True)


@lru_cache(maxsize=1)
def load_meta_map() -> dict[str, str]:
    if not META_PATH.is_file():
        return {}
    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    return {
        str(entry["path"]): str(entry["description"]).strip()
        for entry in data.get("pages", [])
        if entry.get("path") and entry.get("description")
    }


def clip_meta(text: str, *, min_len: int = MIN_LEN, max_len: int = MAX_LEN) -> str:
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[: max_len - 3].rstrip() + "..."
    if len(text) >= min_len:
        return text
    lower = text.lower()
    if "free estimate" in lower or "free written estimate" in lower:
        suffixes = [
            " Knight Group Handyman · Safety Harbor, FL.",
            " Tampa Bay handyman team. Call (813) 649-3341.",
            " Registered and insured in Pinellas County.",
        ]
    else:
        suffixes = [
            " Registered and insured in Pinellas County. Free written estimate.",
            " Knight Group Handyman · Safety Harbor, FL. Free estimate.",
            " Tampa Bay handyman team. Call (813) 649-3341.",
        ]
    for suffix in suffixes:
        if suffix.strip().lower() in lower:
            continue
        candidate = text + suffix
        if min_len <= len(candidate) <= max_len:
            return candidate
    padded = (text + " Free written estimate.").strip()
    if len(padded) > max_len:
        return padded[: max_len - 3].rstrip() + "..."
    return padded


def resolve_description(rel_path: str, fallback: str) -> str:
    mapped = load_meta_map().get(rel_path.replace("\\", "/"))
    if mapped:
        return clip_meta(mapped)
    return clip_meta(fallback)


def social_tags(*, title: str, description: str, canonical: str, twitter_title: str | None = None) -> str:
    tw_title = twitter_title or title
    return f"""    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Knight Group handyman services in Pinellas County, Florida">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@KnightGroupSvcs">
    <meta name="twitter:title" content="{esc(tw_title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{TWITTER_IMAGE}">
    <meta name="twitter:url" content="{esc(canonical)}">"""
