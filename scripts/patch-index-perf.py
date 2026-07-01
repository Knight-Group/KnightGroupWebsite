#!/usr/bin/env python3
"""Patch index.html for Lighthouse performance: responsive images, lazy carousel, deferred map."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PERF = "20260701-perf"

SERVICE_CARD_MAP = {
    "general-repairs.jpg": ("general-repairs", "General repairs service background photo"),
    "kg-leaky-pipes.webp": ("kg-leaky-pipes", "Plumbing services background photo", True),
    "KG-fixture.webp": ("KG-fixture", "Electrical fixture service background photo"),
    "carpentry-framing.jpg": ("carpentry-framing", "Carpentry and framing service background photo"),
    "painting-finishing.jpg": ("painting-finishing", "Painting and finishing service background photo"),
    "home-renovations.jpg": ("home-renovations", "Home renovations service background photo"),
    "kg-door-window-repair.webp": ("kg-door-window-repair", "Doors and windows service background photo"),
    "custom-projects.jpg": ("custom-projects", "Custom projects service background photo"),
    "kg-waterheater-pipe-burst.webp": ("kg-waterheater-pipe-burst", "Emergency handyman service background photo"),
}

GALLERY_FILES = [
    "before-after-fridge-wouldnt-close-does-now.webp",
    "KnightGroupBeforeAfterPipes.webp",
    "KnightGroup_before_after_drain.webp",
    "KnightGroup_before_after_room.webp",
    "before-after-broken-stove-burner-fixed.webp",
    "before-after-broken-blinds-replaced.webp",
    "before-after-horney-removal-wall-sealed.webp",
    "Refinished Bathroom_Window.webp",
    "Refinished_Bathroom.webp",
    "GarbageDisposal.webp",
    "NewTubDrain.webp",
    "fixing_floor2.webp",
    "Moldy_Wall2.webp",
    "Window_Wall2.webp",
    "AC_Vent_Box.webp",
    "Refinished_Room2.webp",
    "fixtures-fans-02.webp",
]


def gallery_src(name: str) -> str:
    stem = name.rsplit(".", 1)[0]
    encoded = name.replace(" ", "%20")
    small = f"/GalleryImages/{stem}-640w.webp"
    full = f"/GalleryImages/{encoded}"
    return (
        f'src="{small}" srcset="{small} 640w, {full} 1200w" '
        f'sizes="(max-width: 1100px) 50vw, 33vw"'
    )


def service_img_tag(slug: str, alt: str, folder: str = "services") -> str:
    if folder == "services":
        small = f"/Images/services/{slug}-400w.webp?v={PERF}"
        large = f"/Images/services/{slug}.webp?v={PERF}"
    else:
        small = f"/Images/{slug}-400w.webp?v={PERF}"
        large = f"/Images/{slug}.webp?v={PERF}"
    return (
        f'<img class="kg-service-card__bg" src="{small}" '
        f'srcset="{small} 400w, {large} 1200w" sizes="(max-width: 900px) 50vw, 280px" '
        f'alt="{alt}" width="400" height="400" loading="lazy" decoding="async">'
    )


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")

    html = re.sub(
        r'    <link rel="preload" as="image" href="/Images/hero-panels/fixed\.webp" media="\(max-width: 768px\)" fetchpriority="high">\n'
        r'    <link rel="preload" as="image" href="/Images/knight-hero-cutout\.webp" media="\(max-width: 768px\)" fetchpriority="high">\n'
        r'    <link rel="preload" as="image" href="/Images/hero-panels/fixed\.webp" media="\(min-width: 769px\)" fetchpriority="high">\n'
        r'    <link rel="preload" as="image" href="/Images/hero-panels/after\.webp" media="\(min-width: 769px\)" fetchpriority="high">\n'
        r'    <link rel="preload" as="image" href="/Images/hero-panels/5e07b6f70709456ca2c12b02ecc44ed9\.webp" media="\(min-width: 769px\)" fetchpriority="high">\n'
        r'    <link rel="preload" as="image" href="/Images/knight-hero-cutout\.webp" media="\(min-width: 769px\)" fetchpriority="high">',
        '    <link rel="preload" as="image" href="/Images/knight-hero-cutout-680w.webp" fetchpriority="high" imagesrcset="/Images/knight-hero-cutout-400w.webp 400w, /Images/knight-hero-cutout-680w.webp 680w, /Images/knight-hero-cutout-960w.webp 960w" imagesizes="(max-width: 760px) 72vw, 340px">',
        html,
    )

    html = html.replace(
        '    <link rel="stylesheet" href="/CSS/kg-redesign.css?v=20260626-carousel-image-fix">',
        f'    <link rel="preload" as="style" href="/CSS/kg-redesign.css?v={PERF}" onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        f'    <noscript><link rel="stylesheet" href="/CSS/kg-redesign.css?v={PERF}"></noscript>',
    )

    html = html.replace(
        """                <picture>
                    <source srcset="/Images/knight-hero-cutout.webp" type="image/webp">
                    <img class="kg-hero-cutout" src="/Images/knight-hero-cutout.png" alt="Vince Knight, owner of Knight Group Handyman Services" width="1200" height="800" decoding="async" fetchpriority="high">
                </picture>""",
        """                <picture>
                    <source type="image/webp" srcset="/Images/knight-hero-cutout-400w.webp 400w, /Images/knight-hero-cutout-680w.webp 680w, /Images/knight-hero-cutout-960w.webp 960w" sizes="(max-width: 760px) 72vw, 340px">
                    <img class="kg-hero-cutout" src="/Images/knight-hero-cutout-680w.webp" alt="Vince Knight, owner of Knight Group Handyman Services" width="680" height="454" decoding="async" fetchpriority="high">
                </picture>""",
    )

    for name in GALLERY_FILES:
        encoded = name.replace(" ", "%20")
        pattern = re.compile(
            rf'<picture><source srcset="/GalleryImages/{re.escape(encoded)}" type="image/webp">'
            rf'<img src="/GalleryImages/{re.escape(encoded)}"([^>]+)></picture>',
            re.I,
        )

        def repl(match: re.Match[str], n=name) -> str:
            attrs = match.group(1)
            attrs = re.sub(r'\sloading="[^"]*"', "", attrs)
            attrs = re.sub(r'\sdata-kg-static="[^"]*"', "", attrs)
            return f'<img {gallery_src(n)}{attrs} loading="lazy" decoding="async" data-kg-carousel-img="true">'

        html = pattern.sub(repl, html)

    for key, spec in SERVICE_CARD_MAP.items():
        slug = spec[0]
        alt = spec[1]
        folder = "services" if key.endswith(".jpg") else "custom"
        new_tag = service_img_tag(slug, alt, folder)
        pattern = re.compile(
            rf'<img class="kg-service-card__bg" src="/Images/(?:services/)?{re.escape(key)}[^"]*"[^>]*>',
            re.I,
        )
        html = pattern.sub(new_tag, html)

    map_old = (
        '                    <div class="kg-map-panel" id="kg-map-shell" aria-label="Knight Group Google map">\n'
        '                        <iframe class="kg-map-frame" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d450975.17752631585!2d-83.16637085978483!3d27.986443383936123!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x88c2ee5d19ac09e7%3A0x98d1805762c6e23c!2sKnight%20Group!5e0!3m2!1sen!2sus!4v1737644902610!5m2!1sen!2sus" title="Knight Group location on Google Maps" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    )
    map_new = (
        '                    <div class="kg-map-panel" id="kg-map-shell" aria-label="Knight Group Google map">\n'
        '                        <button type="button" class="kg-map-load-btn" id="kg-map-load" aria-controls="kg-map-frame">Load interactive map</button>\n'
        '                        <iframe class="kg-map-frame" id="kg-map-frame" title="Knight Group location on Google Maps" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" data-src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d450975.17752631585!2d-83.16637085978483!3d27.986443383936123!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x88c2ee5d19ac09e7%3A0x98d1805762c6e23c!2sKnight%20Group!5e0!3m2!1sen!2sus!4v1737644902610!5m2!1sen!2sus"></iframe>'
    )
    html = html.replace(map_old, map_new)

    html = html.replace(
        'function initMapLoader() { return; }',
        """function initMapLoader() {
            var shell = document.getElementById('kg-map-shell');
            var btn = document.getElementById('kg-map-load');
            var frame = document.getElementById('kg-map-frame');
            if (!shell || !btn || !frame || !frame.dataset.src) return;
            function activate() {
                if (frame.src) return;
                frame.src = frame.dataset.src;
                shell.classList.add('is-map-loaded');
                btn.setAttribute('hidden', 'hidden');
            }
            btn.addEventListener('click', activate);
            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function (entries, obs) {
                    entries.forEach(function (entry) {
                        if (!entry.isIntersecting) return;
                        obs.disconnect();
                    });
                }, { rootMargin: '200px 0px' });
                observer.observe(shell);
            }
        }""",
    )

    html = html.replace(
        """            cards.forEach(function (card) {
                var img = card.querySelector('img');
                if (!img) return;
                img.loading = 'eager';
                img.removeAttribute('data-kg-enter');
                img.removeAttribute('data-kg-enter-immediate');
                img.classList.remove('is-visible');
                img.style.removeProperty('--kg-enter-delay');
            });""",
        """            cards.forEach(function (card, cardIndex) {
                var img = card.querySelector('img');
                if (!img) return;
                img.loading = cardIndex < perView() ? 'eager' : 'lazy';
                img.removeAttribute('data-kg-enter');
                img.removeAttribute('data-kg-enter-immediate');
                img.classList.remove('is-visible');
                img.style.removeProperty('--kg-enter-delay');
            });""",
    )

    html = html.replace("v=20260622-nav-dropdown-anchor", f"v={PERF}")
    html = html.replace("v=20260610-local-trust", f"v={PERF}")
    html = html.replace("v=20260626-carousel-image-fix", f"v={PERF}")
    html = html.replace(
        '    <link rel="stylesheet" href="/CSS/header.min.css?v=20260622-nav-dropdown-anchor">',
        f'    <link rel="stylesheet" href="/CSS/header.min.css?v={PERF}">',
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"Patched {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
