#!/usr/bin/env python3
"""Homepage Lighthouse perf + agentic browsing fixes (CLS, LCP, images, map)."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
ROBOTS = ROOT / "robots.txt"
KG_JS = ROOT / "JS" / "kg-redesign.js"
PERF = "20260719-perf"

GALLERY_DIR = ROOT / "GalleryImages"
HERO_PANELS = ROOT / "Images" / "hero-panels"


def save_webp(src: Path, dest: Path, max_width: int, quality: int = 76) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        img = img.convert("RGB") if img.mode not in ("RGB", "RGBA") else img
        if img.width > max_width:
            ratio = max_width / img.width
            size = (max_width, max(1, round(img.height * ratio)))
            out = img.resize(size, Image.Resampling.LANCZOS)
        else:
            out = img
        out.save(dest, "WEBP", quality=quality, method=6)
    return True


def compress_gallery_assets() -> None:
    """Shrink oversized originals and refresh 640w carousel variants."""
    originals = [
        p
        for p in GALLERY_DIR.glob("*.webp")
        if not re.search(r"-\d+w\.webp$", p.name, re.I)
    ]
    changed = 0
    for src in originals:
        size_kb = src.stat().st_size / 1024
        with Image.open(src) as img:
            width = img.width
        needs = width > 960 or size_kb > 90
        if needs:
            # In-place downscale for gallery detail pages (display ~800 CSS px).
            save_webp(src, src, 960, quality=76)
            changed += 1
            print(f"compressed: {src.name} ({size_kb:.0f}KB -> {src.stat().st_size/1024:.0f}KB)")

        variant = src.with_name(f"{src.stem}-640w.webp")
        save_webp(src, variant, 640, quality=74)
        print(f"640w: {variant.name} ({variant.stat().st_size/1024:.0f}KB)")

    # Heavy hero panel that Lighthouse flagged for compression.
    heavy = HERO_PANELS / "5e07b6f70709456ca2c12b02ecc44ed9.webp"
    if heavy.is_file():
        save_webp(heavy, HERO_PANELS / "5e07b6f70709456ca2c12b02ecc44ed9-720w.webp", 720, quality=68)
        print("recompressed hero panel 5e07…-720w")

    for name in ("after.webp", "fixed.webp", "8616534258664c79aace7cfccd4bec96.webp"):
        src = HERO_PANELS / name
        if src.is_file():
            save_webp(src, src.with_name(f"{src.stem}-720w.webp"), 720, quality=72)

    print(f"Gallery originals recompressed: {changed}")


def gallery_img_tag(src_path: str, attrs: str) -> str:
    name = unquote(src_path.split("/")[-1])
    stem = name.rsplit(".", 1)[0]
    encoded = name.replace(" ", "%20")
    small = f"/GalleryImages/{stem}-640w.webp?v={PERF}"
    full = f"/GalleryImages/{encoded}?v={PERF}"
    # Keep width/height/alt/decoding/data-* from original attrs; normalize loading.
    clean = attrs
    clean = re.sub(r'\sloading="[^"]*"', "", clean)
    clean = re.sub(r'\ssrcset="[^"]*"', "", clean)
    clean = re.sub(r'\ssizes="[^"]*"', "", clean)
    clean = re.sub(r'\sdata-kg-carousel-img="[^"]*"', "", clean)
    if "decoding=" not in clean:
        clean += ' decoding="async"'
    if "width=" not in clean:
        clean += ' width="640" height="480"'
    return (
        f'<img src="{small}" srcset="{small} 640w, {full} 1200w" '
        f'sizes="(max-width: 760px) 92vw, (max-width: 1100px) 46vw, 360px"'
        f'{clean} loading="lazy" data-kg-carousel-img="true">'
    )


def patch_index() -> None:
    html = INDEX.read_text(encoding="utf-8")

    # Remove content-visibility (major CLS source attributed to <main>).
    html = html.replace(
        ".kg-home section:not(.kg-hero){content-visibility:auto;contain-intrinsic-size:0 720px}",
        ".kg-home section:not(.kg-hero){content-visibility:visible}",
    )
    # Align critical header placeholder with real header height (avoids jump).
    html = html.replace(
        "#header-include{min-height:74px}",
        "#header-include{min-height:96px}",
    )

    # Cache-bust CSS/JS for these fixes.
    for old in (
        "20260701-perf",
        "20260701-unified-includes",
        "20260611-glow-shimmer",
    ):
        html = html.replace(f"v={old}", f"v={PERF}")

    # Preload the static LCP hero panel (first slot) + keep cutout.
    html = html.replace(
        '<link rel="preload" as="image" href="/Images/hero-panels/fixed-720w.webp" fetchpriority="high">',
        f'<link rel="preload" as="image" href="/Images/hero-panels/fixed-720w.webp?v={PERF}" fetchpriority="high">\n'
        f'    <link rel="preload" as="image" href="/Images/hero-panels/after-720w.webp?v={PERF}" fetchpriority="high">',
    )

    # Bake stable hero panels into HTML so LCP is discoverable (no lazy, high priority).
    static_panels = f"""            <div class="kg-hero-panels" aria-hidden="true">
                <div class="kg-hero-panel kg-hero-panel--photo kg-hero-panel--left kg-hero-panel--from-left">
                    <img src="/Images/hero-panels/fixed-720w.webp?v={PERF}" alt="" width="720" height="960" decoding="async" loading="eager" fetchpriority="high" role="presentation">
                </div>
                <div class="kg-hero-panel kg-hero-panel--photo kg-hero-panel--top kg-hero-panel--from-top">
                    <img src="/Images/hero-panels/after-720w.webp?v={PERF}" alt="" width="720" height="540" decoding="async" loading="eager" fetchpriority="high" role="presentation">
                </div>
                <div class="kg-hero-panel kg-hero-panel--photo kg-hero-panel--bottom kg-hero-panel--from-bottom">
                    <img src="/Images/hero-panels/5e07b6f70709456ca2c12b02ecc44ed9-720w.webp?v={PERF}" alt="" width="720" height="540" decoding="async" loading="lazy" role="presentation">
                </div>
                <div class="kg-hero-panel kg-hero-panel--photo kg-hero-panel--right kg-hero-panel--from-right">
                    <img src="/Images/hero-panels/8616534258664c79aace7cfccd4bec96-720w.webp?v={PERF}" alt="" width="720" height="960" decoding="async" loading="lazy" role="presentation">
                </div>
            </div>"""
    html = re.sub(
        r'<div class="kg-hero-panels" aria-hidden="true"></div>',
        static_panels,
        html,
        count=1,
    )
    # Mark hero ready immediately so panels don't wait on JS for paint.
    html = html.replace(
        '<section class="kg-hero" data-hero-panels>',
        '<section class="kg-hero kg-hero-panels-ready" data-hero-panels data-hero-panels-static="1">',
    )

    # Convert every gallery <picture>…</picture> in the job carousel to responsive 640w.
    picture_re = re.compile(
        r'<picture><source srcset="(/GalleryImages/[^"]+\.webp)" type="image/webp">'
        r'<img src="/GalleryImages/[^"]+\.webp"([^>]*)></picture>',
        re.I,
    )

    def repl_picture(match: re.Match[str]) -> str:
        return gallery_img_tag(match.group(1), match.group(2))

    html, n_pics = picture_re.subn(repl_picture, html)
    print(f"Carousel pictures rewritten: {n_pics}")

    # Click-to-load Google Maps (kills ~400KB unused Maps JS on initial load).
    html = re.sub(
        r'<div class="kg-map-panel" id="kg-map-shell" aria-label="Knight Group Google map">\s*'
        r'<iframe class="kg-map-frame" id="kg-map-frame"[^>]*src="([^"]+)"[^>]*></iframe>',
        (
            '<div class="kg-map-panel" id="kg-map-shell" aria-label="Knight Group Google map">\n'
            '                        <button type="button" class="kg-map-load-btn" id="kg-map-load" aria-controls="kg-map-frame">Load interactive map</button>\n'
            '                        <iframe class="kg-map-frame" id="kg-map-frame" title="Knight Group location on Google Maps" '
            'allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade" data-src="\\1"></iframe>'
        ),
        html,
        count=1,
        flags=re.S,
    )

    map_loader = """        function initMapLoader() {
            var shell = document.getElementById('kg-map-shell');
            var btn = document.getElementById('kg-map-load');
            var frame = document.getElementById('kg-map-frame');
            if (!shell || !btn || !frame || !frame.dataset.src) return;
            function activate() {
                if (frame.getAttribute('src')) return;
                frame.src = frame.dataset.src;
                shell.classList.add('is-map-loaded');
                btn.setAttribute('hidden', 'hidden');
            }
            btn.addEventListener('click', activate);
        }"""
    html = re.sub(
        r"        function initMapLoader\(\) \{ return; \}",
        map_loader,
        html,
        count=1,
    )

    # Only first viewport of carousel should be eager.
    html = re.sub(
        r'(data-kg-carousel-img="true">)',
        r'\1',
        html,
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"Patched {INDEX.relative_to(ROOT)}")


def patch_kg_js() -> None:
    js = KG_JS.read_text(encoding="utf-8")

    # If panels were baked into HTML, do not wipe/reshuffle them (LCP + CLS stability).
    guard = """  function initHeroPanels() {
    var hero = document.querySelector('.kg-home .kg-hero[data-hero-panels]');
    if (!hero || hero.dataset.heroPanelsInit) return;
    hero.dataset.heroPanelsInit = '1';

    if (hero.getAttribute('data-hero-panels-static') === '1') {
      hero.classList.add('kg-hero-panels-ready');
      revealImmediate();
      syncHeroColumnHeights();
      return;
    }

    renderHeroPanels(hero, heroFallbackImages());
"""
    js = re.sub(
        r"  function initHeroPanels\(\) \{\n"
        r"    var hero = document\.querySelector\('\.kg-home \.kg-hero\[data-hero-panels\]'\);\n"
        r"    if \(!hero \|\| hero\.dataset\.heroPanelsInit\) return;\n"
        r"    hero\.dataset\.heroPanelsInit = '1';\n\n"
        r"    renderHeroPanels\(hero, heroFallbackImages\(\)\);",
        guard.rstrip(),
        js,
        count=1,
    )

    # Soften first-paint height sync thrash: defer noncritical sync slightly.
    js = js.replace(
        "    queueSync();\n\n    if (typeof ResizeObserver !== 'undefined') {",
        "    if ('requestIdleCallback' in window) {\n"
        "      requestIdleCallback(queueSync, { timeout: 1200 });\n"
        "    } else {\n"
        "      setTimeout(queueSync, 0);\n"
        "    }\n\n    if (typeof ResizeObserver !== 'undefined') {",
        1,
    )

    KG_JS.write_text(js, encoding="utf-8")
    print(f"Patched {KG_JS.relative_to(ROOT)}")


def patch_robots() -> None:
    text = ROBOTS.read_text(encoding="utf-8")
    if "llms.txt" not in text:
        text = text.replace(
            "Sitemap: https://www.knightgroup.com/sitemap.xml",
            "Sitemap: https://www.knightgroup.com/sitemap.xml\n\n"
            "# AI / agent discovery\n"
            "# https://www.knightgroup.com/llms.txt\n"
            "# https://www.knightgroup.com/ai.txt",
        )
        ROBOTS.write_text(text, encoding="utf-8")
        print("Patched robots.txt with llms.txt pointers")
    else:
        print("robots.txt already references llms.txt")


def mark_first_carousel_eager(html: str) -> str:
    """After all carousel imgs are lazy, mark the first 3 as eager for desktop."""
    count = {"n": 0}

    def repl(match: re.Match[str]) -> str:
        count["n"] += 1
        tag = match.group(0)
        if count["n"] <= 3:
            return tag.replace('loading="lazy"', 'loading="eager"')
        return tag

    return re.sub(
        r'<img src="/GalleryImages/[^"]+-640w\.webp[^"]*"[^>]*data-kg-carousel-img="true">',
        repl,
        html,
    )


def main() -> int:
    compress_gallery_assets()
    patch_index()
    html = INDEX.read_text(encoding="utf-8")
    html = mark_first_carousel_eager(html)
    INDEX.write_text(html, encoding="utf-8")
    patch_kg_js()
    patch_robots()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
