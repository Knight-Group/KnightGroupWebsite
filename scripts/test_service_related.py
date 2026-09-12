"""Related-card image uniqueness and gallery-cover mapping."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from service_related import (  # noqa: E402
    after_still_web_path,
    assign_unique_related_srcs,
    gallery_cover_src,
    is_face_card_src,
    related_card_src,
    rewrite_related_grids,
    src_key,
)


def test_after_still_web_path():
    assert (
        after_still_web_path("fence-and-garage-5544008-before-after")
        == "/GalleryImages/after-fence-and-garage-5544008.webp"
    )


def test_gallery_href_uses_job_cover():
    src = related_card_src("/gallery/fence-and-garage-5544008-before-after")
    assert "fence-and-garage-5544008" in src
    assert "handyman.webp" not in src
    still = after_still_web_path("fence-and-garage-5544008-before-after")
    if src_key(src) == src_key(still):
        assert gallery_cover_src("/gallery/fence-and-garage-5544008-before-after") == still
    else:
        assert "before-after-fence-and-garage-5544008" in src
    front = gallery_cover_src("/gallery/front-fence-repair-08fc100-before-after")
    assert front
    assert "front-fence-repair-08fc100" in front


def test_related_grid_does_not_repeat_src():
    links = [
        ("/gallery/fence-and-garage-5544008-before-after", "Fence and Garage"),
        ("/gallery/front-fence-repair-08fc100-before-after", "Front fence repair"),
        ("/about", "About Knight Group"),
        ("/handyman-scope-florida", "Handyman scope in Florida"),
        ("/Services/handyman", "Handyman services"),
        ("/pricing", "Handyman pricing"),
    ]
    assigned = assign_unique_related_srcs(
        links,
        reserved=["/Images/services/home-renovations.webp"],
    )
    keys = [src_key(src) for _href, _label, src in assigned]
    assert len(keys) == len(set(keys))
    assert "handyman.webp" not in "".join(keys[0:2])
    about = next(src for href, _label, src in assigned if href == "/about")
    assert is_face_card_src(about)


def test_plumbing_cards_keep_plumbing_photos():
    assigned = assign_unique_related_srcs(
        [
            ("/plumber-background-handyman", "Journeyman plumbing experience"),
            ("/Services/plumbing-services", "Plumbing assessment"),
            ("/about", "About Knight Group"),
            ("/booking", "Get a free written estimate"),
            ("/Services/handyman", "Handyman services"),
        ]
    )
    keys = [src_key(src) for _href, _label, src in assigned]
    assert len(keys) == len(set(keys))
    plumber = next(src for href, _label, src in assigned if href == "/plumber-background-handyman")
    plumbing = next(src for href, _label, src in assigned if href == "/Services/plumbing-services")
    handyman = next(src for href, _label, src in assigned if href == "/Services/handyman")
    about = next(src for href, _label, src in assigned if href == "/about")
    booking = next(src for href, _label, src in assigned if href == "/booking")
    assert "cabinet-repair-339b0d9" in plumber
    assert "facuet-replacement" in plumbing
    assert "handyman.webp" not in handyman
    assert "general-repairs.webp" not in plumber
    assert "general-repairs.webp" not in plumbing
    assert "plumbing-services.webp" not in plumber
    assert is_face_card_src(about)
    assert "Knight-Hammer" in booking


def test_rewrite_related_grids_replaces_duplicate_handyman_webp():
    html = """
            <img src="/Images/services/home-renovations.webp" alt="hero">
            <div class="kg-service-related-grid">
                        <a class="kg-service-related-card" href="/gallery/fence-and-garage-5544008-before-after">
                            <img src="/Images/services/handyman.webp?v=old" alt="Fence and Garage" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">Fence and Garage</span>
                        </a>
                        <a class="kg-service-related-card" href="/gallery/front-fence-repair-08fc100-before-after">
                            <img src="/Images/services/handyman.webp?v=old" alt="Front fence repair" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">Front fence repair</span>
                        </a>
                        <a class="kg-service-related-card" href="/about">
                            <img src="/Images/KGHero_person_crop_1200x1600.jpg?v=old" alt="About Knight Group" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">About Knight Group</span>
                        </a>
                        <a class="kg-service-related-card" href="/handyman-scope-florida">
                            <img src="/Images/services/handyman.webp?v=old" alt="Handyman scope in Florida" width="400" height="300" loading="lazy" decoding="async">
                            <span class="kg-service-related-card__label">Handyman scope in Florida</span>
                        </a>
                    </div>
"""
    out = rewrite_related_grids(html, version="20260829-after-stills")
    assert 'href="/gallery/fence-and-garage-5544008-before-after"' in out
    assert "fence-and-garage-5544008.webp" in out
    assert "front-fence-repair-08fc100.webp" in out
    assert "kg-service-related-card--face" in out
    srcs = [line.split('src="', 1)[1].split("?", 1)[0] for line in out.splitlines() if "<img src=" in line]
    related = srcs[1:]
    assert len(related) == len(set(related))
    assert related.count("/Images/services/handyman.webp") <= 1


if __name__ == "__main__":
    test_after_still_web_path()
    test_gallery_href_uses_job_cover()
    test_related_grid_does_not_repeat_src()
    test_plumbing_cards_keep_plumbing_photos()
    test_rewrite_related_grids_replaces_duplicate_handyman_webp()
    print("ok")
