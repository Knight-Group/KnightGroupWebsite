"""Gallery longform uniqueness, length, and PII guards."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gallery_longform import MIN_WORDS, build_gallery_longform  # noqa: E402
from gallery_public_web import strip_html_words  # noqa: E402
from gallery_scope import gallery_should_index  # noqa: E402


def _fence(slug: str, city: str, worker: str, notes: str) -> dict:
    return {
        "id": slug,
        "title": "Fence is falling down and needs to be put back up — before & after",
        "description": "Before-and-after proof",
        "cluster": "fence",
        "workerName": worker,
        "workerRole": "co-owner and Field Operations Lead",
        "workerKey": "vince" if "Vince" in worker else "tech",
        "cityName": city,
        "citySlug": city.lower().replace(" ", "-"),
        "countyName": "Pasco County" if "Richey" in city else "Pinellas County",
        "completedMonth": "August 2026",
        "workNotes": notes,
        "photoBefore": 3,
        "photoProcess": 2,
        "photoAfter": 3,
        "serviceLink": "/Services/carpentry-framing",
    }


def test_longform_meets_word_count_and_is_unique():
    a = build_gallery_longform(
        _fence(
            "fence-is-falling-down-and-needs-to-be-pu-b17b3ec-before-after",
            "Port Richey",
            "Vince Knight",
            "Reset leaning privacy panels and refastened the rails that had pulled free.",
        )
    )
    b = build_gallery_longform(
        _fence(
            "fence-repair-other-aaaaaaa-before-after",
            "Holiday",
            "Nicholas Alexopoulos",
            "Replaced a failed corner post and rebuilt the adjoining picket run.",
        )
    )
    assert a["word_count"] >= MIN_WORDS
    assert b["word_count"] >= MIN_WORDS
    assert strip_html_words(a["body_html"]) >= MIN_WORDS
    assert a["body_html"] != b["body_html"]
    assert "Vince Knight" in a["body_html"]
    assert "Nicholas Alexopoulos" in b["body_html"]
    assert "Port Richey" in a["body_html"]
    assert "Holiday" in b["body_html"]
    assert "/Services/carpentry-framing" in a["body_html"]
    assert "/booking" in a["body_html"]
    assert "/llms.txt" in a["body_html"]
    assert "kg-howto-steps" in a["body_html"]


def test_longform_strips_ticket_pii():
    group = _fence(
        "fence-pii-bbbbbbb-before-after",
        "Port Richey",
        "Vince Knight",
        "Work at 7324 Parrot Dr billed $263.39 ticket KG-20260816-809A",
    )
    # Catalog should already be clean; generator still sweeps HTML.
    group["workNotes"] = "Reset the leaning run and refastened rails that had pulled from the posts."
    html = build_gallery_longform(group)["body_html"].lower()
    assert "7324" not in html
    assert "parrot dr" not in html
    assert "263.39" not in html
    assert "kg-20260816" not in html
    assert "copeland" not in html
    assert "(813) 649-3341" in html


def test_dispatch_pages_are_indexable_except_vendor_titles():
    curated = {"fence-repair-before-after"}
    assert gallery_should_index(
        {"id": "fence-is-falling-down-and-needs-to-be-pu-b17b3ec-before-after", "title": "Fence"},
        curated,
    )
    assert not gallery_should_index(
        {"id": "copeland-morgan-llc-work-order-before-after", "title": "Copeland Morgan LLC: Work order"},
        curated,
    )
    assert gallery_should_index({"id": "fence-repair-before-after", "title": "Fence"}, curated)


if __name__ == "__main__":
    test_longform_meets_word_count_and_is_unique()
    test_longform_strips_ticket_pii()
    test_dispatch_pages_are_indexable_except_vendor_titles()
    print("gallery longform tests passed")
