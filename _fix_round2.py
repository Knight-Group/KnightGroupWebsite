"""
Round 2 fix script — KnightGroup website
Fixes:
  1. GTM deferred on all non-homepage HTML pages (TBT reduction)
  2. openingHoursSpecification standardized to Mo-Fr 08:00-17:00 (plumbing, electrical)
  3. Title tags trimmed to ≤60 chars (11 pages)
  4. Contact form autocomplete attributes
  5. robots.txt — add corrupted backup files
  6. _headers CSP — add Clarity domains
  7. carpentry-framing.html — fix sameAs URLs
  8. Skip-nav link in header.html + id="main-content" on service page <main> tags
"""

import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix(path, fn):
    fullpath = os.path.join(ROOT, path)
    original = read(fullpath)
    updated = fn(original)
    if updated != original:
        write(fullpath, updated)
        print(f'  [FIXED] {path}')
    else:
        print(f'  [skip]  {path} — no change needed')

# ──────────────────────────────────────────────────────────────
# 1. GTM — DEFERRED PATTERN
# ──────────────────────────────────────────────────────────────

GTM_DEFERRED = (
    '<!-- Google Tag Manager — deferred after load to reduce TBT -->\n'
    '    <script>window.dataLayer = window.dataLayer || [];</script>\n'
    '    <script>\n'
    '    window.addEventListener(\'load\', function() {\n'
    '        var s = document.createElement(\'script\');\n'
    '        s.src = \'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG\';\n'
    '        s.async = true;\n'
    '        document.head.appendChild(s);\n'
    '        window.dataLayer.push({\'gtm.start\': new Date().getTime(), event: \'gtm.js\'});\n'
    '    });\n'
    '    </script>\n'
    '    <!-- End Google Tag Manager -->'
)

# Matches any <!-- Google Tag Manager --> ... <script>...</script> ... <!-- End Google Tag Manager -->
GTM_PATTERN = re.compile(
    r'<!-- Google Tag Manager -->[ \t]*\n?\s*<script>[\s\S]*?</script>\s*\n?\s*<!-- End Google Tag Manager -->',
    re.MULTILINE
)

def defer_gtm(content):
    return GTM_PATTERN.sub(GTM_DEFERRED, content)

GTM_PAGES = [
    'about.html',
    'contact.html',
    'galleries.html',
    'pricing.html',
    'Services/carpentry-framing.html',
    'Services/custom-projects.html',
    'Services/doors-windows.html',
    'Services/electrical-work.html',
    'Services/emergency-services.html',
    'Services/general-repairs.html',
    'Services/handyman.html',
    'Services/home-renovations.html',
    'Services/painting-finishing.html',
    'Services/plumbing-services.html',
]

print('\n=== 1. GTM — DEFER ===')
for p in GTM_PAGES:
    fix(p, defer_gtm)

# ──────────────────────────────────────────────────────────────
# 2. openingHoursSpecification — normalize plumbing & electrical
# ──────────────────────────────────────────────────────────────

# These two pages have 7-day 07:00-19:00 — change to Mo-Fr 08:00-17:00
OLD_HOURS_PATTERN = re.compile(
    r'"openingHoursSpecification":\s*\{\s*'
    r'"@type":\s*"OpeningHoursSpecification",\s*'
    r'"dayOfWeek":\s*\[\s*"Monday",\s*"Tuesday",\s*"Wednesday",\s*"Thursday",\s*"Friday",\s*"Saturday",\s*"Sunday"\s*\],\s*'
    r'"opens":\s*"07:00",\s*"closes":\s*"19:00"\s*\}',
    re.DOTALL
)

NEW_HOURS = (
    '"openingHoursSpecification": {\n'
    '        "@type": "OpeningHoursSpecification",\n'
    '        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],\n'
    '        "opens": "08:00",\n'
    '        "closes": "17:00"\n'
    '      }'
)

def fix_hours(content):
    return OLD_HOURS_PATTERN.sub(NEW_HOURS, content)

HOURS_PAGES = [
    'Services/plumbing-services.html',
    'Services/electrical-work.html',
]

print('\n=== 2. openingHoursSpecification ===')
for p in HOURS_PAGES:
    fix(p, fix_hours)

# ──────────────────────────────────────────────────────────────
# 3. TITLE TAGS — trim to ≤60 chars
# ──────────────────────────────────────────────────────────────

TITLE_FIXES = {
    'about.html': (
        '<title>About Knight Group | Handyman Services Pinellas County, FL \u2014 15+ Years</title>',
        '<title>About Knight Group | Handyman, Pinellas County FL</title>'
    ),
    'contact.html': (
        '<title>Contact Knight Group | Free Handyman Estimate in Pinellas County, FL</title>',
        '<title>Contact Knight Group Handyman | Pinellas County, FL</title>'
    ),
    'pricing.html': (
        '<title>Pricing | Knight Group Professional Handyman Services in Pinellas County, FL</title>',
        '<title>Handyman Pricing Guide | Knight Group, Pinellas County</title>'
    ),
    'Services/handyman.html': (
        '<title>Handyman Services | Knight Group Handyman Services LLC | Pinellas County</title>',
        '<title>Local Handyman Services Pinellas County, FL | Knight Group</title>'
    ),
    'Services/electrical-work.html': (
        '<title>Electrical Work Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>Electrical Work Pinellas County, FL | Knight Group</title>'
    ),
    'Services/general-repairs.html': (
        '<title>General Repairs Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>General Repairs Pinellas County, FL | Knight Group</title>'
    ),
    'Services/home-renovations.html': (
        '<title>Home Renovations Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>Home Renovations Pinellas County, FL | Knight Group</title>'
    ),
    'Services/painting-finishing.html': (
        '<title>Painting Services Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>Painting Services Pinellas County, FL | Knight Group</title>'
    ),
    'Services/plumbing-services.html': (
        '<title>Plumbing Services Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>Plumbing Services Pinellas County, FL | Knight Group</title>'
    ),
    'Services/custom-projects.html': (
        '<title>Custom Projects Pinellas County, FL | Knight Group Handyman Services</title>',
        '<title>Custom Projects Pinellas County, FL | Knight Group</title>'
    ),
    'Services/doors-windows.html': (
        '<title>Door &amp; Window Installation Pinellas County, FL | Knight Group Handyman</title>',
        '<title>Doors &amp; Windows Pinellas County, FL | Knight Group</title>'
    ),
}

print('\n=== 3. TITLE TAGS ===')
for page, (old, new) in TITLE_FIXES.items():
    def make_title_fn(o, n):
        def fn(content):
            return content.replace(o, n)
        return fn
    fix(page, make_title_fn(old, new))

# ──────────────────────────────────────────────────────────────
# 4. CONTACT FORM — autocomplete attributes
# ──────────────────────────────────────────────────────────────

def fix_contact_autocomplete(content):
    content = content.replace(
        '<input type="text" id="name" name="name" required>',
        '<input type="text" id="name" name="name" autocomplete="name" required>'
    )
    content = content.replace(
        '<input type="tel" id="phone" name="phone" required>',
        '<input type="tel" id="phone" name="phone" autocomplete="tel" required>'
    )
    content = content.replace(
        '<input type="email" id="email" name="email" required>',
        '<input type="email" id="email" name="email" autocomplete="email" required>'
    )
    content = content.replace(
        '<input type="text" id="address" name="address" placeholder="Street address for service location">',
        '<input type="text" id="address" name="address" autocomplete="street-address" placeholder="Street address for service location">'
    )
    return content

print('\n=== 4. CONTACT FORM AUTOCOMPLETE ===')
fix('contact.html', fix_contact_autocomplete)

# ──────────────────────────────────────────────────────────────
# 5. ROBOTS.TXT — add corrupted backup files
# ──────────────────────────────────────────────────────────────

ROBOTS_ADDITIONS = (
    'Disallow: /_carpentry_corrupted\n'
    'Disallow: /_carpentry_corrupted.html\n'
    'Disallow: /_handyman_corrupted\n'
    'Disallow: /_handyman_corrupted.html\n'
)

def fix_robots(content):
    if '_carpentry_corrupted' in content:
        return content  # already added
    # Insert before the Sitemap line at the end
    return content.replace(
        '\nSitemap: https://www.knightgroup.com/sitemap.xml',
        '\n' + ROBOTS_ADDITIONS + '\nSitemap: https://www.knightgroup.com/sitemap.xml'
    )

print('\n=== 5. ROBOTS.TXT ===')
fix('robots.txt', fix_robots)

# ──────────────────────────────────────────────────────────────
# 6. _HEADERS CSP — add Microsoft Clarity domains
# ──────────────────────────────────────────────────────────────

def fix_headers_csp(content):
    # Add Clarity to script-src
    content = content.replace(
        'https://maps.gstatic.com; style-src',
        'https://maps.gstatic.com https://www.clarity.ms; style-src'
    )
    # Add Clarity to connect-src
    content = content.replace(
        'https://www.googletagmanager.com; object-src',
        'https://www.googletagmanager.com https://www.clarity.ms; object-src'
    )
    # Add Clarity to img-src (session recording may send image beacons)
    content = content.replace(
        'https://lh3.googleusercontent.com; frame-src',
        'https://lh3.googleusercontent.com https://www.clarity.ms; frame-src'
    )
    return content

print('\n=== 6. _HEADERS CSP ===')
fix('_headers', fix_headers_csp)

# ──────────────────────────────────────────────────────────────
# 7. CARPENTRY-FRAMING — fix sameAs URLs
# ──────────────────────────────────────────────────────────────

def fix_carpentry_sameas(content):
    old_sameas = (
        '"sameAs": [\n'
        '                    "https://www.facebook.com/people/Knight-Group/61556138899838/",\n'
        '                    "https://www.instagram.com/knightgroup.biz/",\n'
        '                    "https://discord.com/invite/kwNPMPVqc8"\n'
        '                ]'
    )
    new_sameas = (
        '"sameAs": [\n'
        '                    "https://www.facebook.com/KnightGroupServices/",\n'
        '                    "https://www.instagram.com/knight_group_services/"\n'
        '                ]'
    )
    return content.replace(old_sameas, new_sameas)

print('\n=== 7. CARPENTRY-FRAMING sameAs ===')
fix('Services/carpentry-framing.html', fix_carpentry_sameas)

# ──────────────────────────────────────────────────────────────
# 8. SKIP NAV — add to header.html + id="main-content" on service pages
# ──────────────────────────────────────────────────────────────

SKIP_NAV_CSS = (
    '.skip-nav {\n'
    '    position: absolute;\n'
    '    left: -10000px;\n'
    '    top: auto;\n'
    '    width: 1px;\n'
    '    height: 1px;\n'
    '    overflow: hidden;\n'
    '    z-index: 9999;\n'
    '}\n'
    '.skip-nav:focus {\n'
    '    position: fixed;\n'
    '    left: 50%;\n'
    '    top: 12px;\n'
    '    transform: translateX(-50%);\n'
    '    width: auto;\n'
    '    height: auto;\n'
    '    overflow: visible;\n'
    '    background: #800000;\n'
    '    color: #fff;\n'
    '    padding: 10px 20px;\n'
    '    border-radius: 6px;\n'
    '    font-weight: 600;\n'
    '    font-size: 1rem;\n'
    '    text-decoration: none;\n'
    '    box-shadow: 0 4px 16px rgba(0,0,0,0.3);\n'
    '    outline: 3px solid #fff;\n'
    '    z-index: 9999;\n'
    '}\n'
)

def fix_header_skipnav(content):
    # Add skip-nav CSS into the first <style> block
    if 'skip-nav' in content:
        return content
    content = content.replace(
        '/* ============================\n   HEADER — DESKTOP\n   ============================ */',
        SKIP_NAV_CSS + '/* ============================\n   HEADER — DESKTOP\n   ============================ */'
    )
    # Add skip-nav link as first element inside <header>
    content = content.replace(
        '<header>\n    <div class="container">',
        '<a href="#main-content" class="skip-nav">Skip to main content</a>\n<header>\n    <div class="container">'
    )
    return content

print('\n=== 8a. HEADER — skip-nav link ===')
fix('header.html', fix_header_skipnav)

# Add id="main-content" to <main> tags on service pages that lack it
MAIN_PAGES = [
    'Services/carpentry-framing.html',
    'Services/custom-projects.html',
    'Services/doors-windows.html',
    'Services/electrical-work.html',
    'Services/emergency-services.html',
    'Services/general-repairs.html',
    'Services/handyman.html',
    'Services/home-renovations.html',
    'Services/painting-finishing.html',
    'Services/plumbing-services.html',
    'about.html',
    'contact.html',
    'pricing.html',
    'galleries.html',
]

def add_main_id(content):
    # Only replace bare <main> (with optional whitespace before >) that has no id
    if 'id="main-content"' in content:
        return content
    return re.sub(r'<main(?:\s+(?!id=)[^>]*)?>(?!\s*</main>)', lambda m: m.group(0).rstrip('>') + ' id="main-content">', content, count=1)

print('\n=== 8b. id="main-content" on <main> tags ===')
for p in MAIN_PAGES:
    fix(p, add_main_id)

print('\n=== DONE ===')
