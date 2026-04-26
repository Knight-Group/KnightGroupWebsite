import re, os

ROOT = os.getcwd()

def read(p): return open(p, encoding='utf-8').read()
def write(p, c): open(p, 'w', encoding='utf-8').write(c)
def fix(p, fn):
    orig = read(p); updated = fn(orig)
    if updated != orig: write(p, updated); print(f'  [FIXED] {p}')
    else: print(f'  [skip]  {p}')

# 1. Remove dead body.dark-mode CSS blocks from every page
DARK_MODE_RE = re.compile(r'\n[ \t]*body\.dark-mode[^{]*\{[^}]*\}', re.DOTALL)

def strip_dark_mode(content):
    return DARK_MODE_RE.sub('', content)

dark_pages = [
    'Services/carpentry-framing.html', 'Services/custom-projects.html',
    'Services/doors-windows.html', 'Services/electrical-work.html',
    'Services/emergency-services.html', 'Services/general-repairs.html',
    'Services/handyman.html', 'Services/home-renovations.html',
    'Services/painting-finishing.html', 'Services/plumbing-services.html',
    'about.html', 'contact.html', 'galleries.html', 'pricing.html',
]
print('=== 1. Strip dead dark-mode CSS ===')
for p in dark_pages:
    fix(p, strip_dark_mode)

# 2. Add defer to includes.js where missing
def add_defer_service(content):
    return content.replace(
        'src="../JS/includes.js">', 'src="../JS/includes.js" defer>'
    )

def add_defer_root(content):
    return content.replace(
        'src="JS/includes.js">', 'src="JS/includes.js" defer>'
    )

service_no_defer = [
    'Services/electrical-work.html',
    'Services/plumbing-services.html',
    'Services/emergency-services.html',
]
policy_no_defer = [
    'PolicyPages/terms.html',
    'PolicyPages/payment-policy.html',
    'PolicyPages/returnpolicy.html',
    'PolicyPages/privacy-policy.html',
]
print('\n=== 2. Add defer to includes.js ===')
for p in service_no_defer:
    fix(p, add_defer_service)
for p in policy_no_defer:
    fix(p, add_defer_service)
fix('pricing.html', add_defer_root)

# 3. Fix handyman.html Formspree ID
def fix_handyman_formspree(content):
    return content.replace('formspree.io/f/mvgogaaw', 'formspree.io/f/xzzvnpne')
print('\n=== 3. Fix handyman Formspree ID ===')
fix('Services/handyman.html', fix_handyman_formspree)

# 4. Footer copyright year
def fix_footer_year(content):
    return content.replace('1995 - 2025', '1995 - 2026')
print('\n=== 4. Footer copyright year ===')
fix('footer.html', fix_footer_year)

print('\nDONE')
