#!/usr/bin/env python3
"""Shared classification for historical gallery work with regulated scope."""

from __future__ import annotations

import re


REGULATED_GALLERY_TERMS = re.compile(
    r"ceiling[- ]fan|light[- ]fixture|ballast|(?:wall |secure )?outlets?|electrical|"
    r"plumb|pipe[- ]repair|drain|faucet|facuet|garbage[- ]disposal|toilets?|"
    r"hot water|water leaks?|\bshower\b|a/?c service|air conditioning|hvac service|airflow service|"
    r"bathroom remodel|tub surround|mold|wasps?|bee nest|pest control",
    re.I,
)


def is_regulated_gallery_group(group: dict) -> bool:
    """Return True when the project's current equivalent may require licensed scope."""
    if group.get("serviceLink") in {"/Services/electrical-work", "/Services/plumbing-services"}:
        return True
    searchable = " ".join(
        str(group.get(key, ""))
        for key in ("id", "@id", "title", "name", "description", "serviceLink")
    )
    return bool(REGULATED_GALLERY_TERMS.search(searchable))
