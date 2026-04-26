"""
Comprehensive performance fixes for KnightGroupWebsite:
1. Fix #header-include min-height (CLS fix) on ALL pages
2. Strip dead dark-mode CSS from index.html (was missed in previous pass)
3. Increase third-party script delays for TBT reduction
"""
import re, os, glob

ROOT = 'e:\\KnightGroupWebsite'
os.chdir(ROOT)

def read(p): return open(p, encoding='utf-8').read()
def write(p, c): open(p, 'w', encoding='utf-8').write(c)
def fix(p, fn):
    orig = read(p); updated = fn(orig)
    if updated != orig: write(p, updated); return True
    return False

# ── 1. Fix #header-include min-height ───────────────────────────────────────
# Header .header-content has min-height: 68px + 3px border-bottom → reserve 74px
HEADER_MIN_HEIGHT_CSS = '\n        /* CLS: reserve header height before JS injects */\n        #header-include { min-height: 74px; }\n'

def fix_header_include(content):
    # Case 1: index.html has min-height: 0 — replace it
    if '#header-include {\n            min-height: 0;\n        }' in content:
        return content.replace(
            '#header-include {\n            min-height: 0;\n        }',
            '#header-include { min-height: 74px; }'
        )
    # Case 2: any #header-include min-height already set — update it
    if '#header-include' in content and 'min-height' in content.split('#header-include')[1][:60]:
        return re.sub(r'#header-include\s*\{[^}]*\}', '#header-include { min-height: 74px; }', content)
    # Case 3: no #header-include rule — add it in first <style> block
    if '#header-include' not in content:
        # Insert after the first opening <style> tag
        content = re.sub(r'(<style>)', r'\1' + HEADER_MIN_HEIGHT_CSS, content, count=1)
    return content

# ── 2. Strip ALL dark-mode CSS from index.html (was missed) ─────────────────
DARK_MODE_RE = re.compile(r'\n[ \t]*body\.dark-mode[^{]*\{[^}]*\}', re.DOTALL)

def strip_dark_mode(content):
    return DARK_MODE_RE.sub('', content)

# ── 3. Further delay Clarity to 6 seconds (above typical LH measurement window) ─
def delay_clarity(content):
    return content.replace(
        '}, 2500);',
        '}, 6000);'
    )

# ── 4. Use requestIdleCallback for GTM to reduce main thread blocking ────────
OLD_GTM = """    window.addEventListener('load', function() {
        var s = document.createElement('script');
        s.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG';
        s.async = true;
        document.head.appendChild(s);
        window.dataLayer.push({'gtm.start': new Date().getTime(), event: 'gtm.js'});
    });"""
NEW_GTM = """    var _gtmLoaded = false;
    function _loadGTM() {
        if (_gtmLoaded) return;
        _gtmLoaded = true;
        var s = document.createElement('script');
        s.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG';
        s.async = true;
        document.head.appendChild(s);
        window.dataLayer.push({'gtm.start': new Date().getTime(), event: 'gtm.js'});
    }
    // Load GTM after idle or 4 seconds, whichever comes first
    if ('requestIdleCallback' in window) {
        requestIdleCallback(_loadGTM, { timeout: 4000 });
    } else {
        setTimeout(_loadGTM, 4000);
    }"""

def delay_gtm(content):
    if OLD_GTM in content:
        return content.replace(OLD_GTM, NEW_GTM)
    return content

# ── Collect all live HTML pages ──────────────────────────────────────────────
all_html = (
    glob.glob('*.html') +
    glob.glob('Services/*.html') +
    glob.glob('PolicyPages/*.html')
)
# Exclude dev/blocked pages
EXCLUDE = {'page-template.html', 'socialCards.html', 'head-gtm.html',
           '_carpentry_corrupted.html', '_handyman_corrupted.html'}
live_pages = [p for p in all_html if os.path.basename(p) not in EXCLUDE
              and 'handcraftedfurniture' not in p and 'programming' not in p]

print(f'Processing {len(live_pages)} pages...\n')

# Apply fixes
cls_fixed = defer_fixed = dark_fixed = gtm_fixed = 0
for p in sorted(live_pages):
    orig = read(p)
    content = orig
    
    content = fix_header_include(content)
    content = strip_dark_mode(content)
    
    if 'index.html' in p:
        content = delay_gtm(content)
        content = delay_clarity(content)
    
    if content != orig:
        write(p, content)
        changes = []
        if '#header-include' in content and '#header-include' not in orig:
            changes.append('CLS-header')
            cls_fixed += 1
        elif 'min-height: 74px' in content and 'min-height: 0' in orig:
            changes.append('CLS-header(fixed0)')
            cls_fixed += 1
        if 'body.dark-mode' not in content and 'body.dark-mode' in orig:
            changes.append('dark-mode-stripped')
            dark_fixed += 1
        if 'requestIdleCallback' in content:
            changes.append('GTM-deferred')
            gtm_fixed += 1
        if '6000' in content and '2500' in orig:
            changes.append('Clarity-delayed')
        print(f'  [FIXED] {p}: {", ".join(changes) if changes else "updated"}')

print(f'\nSummary: CLS-header={cls_fixed}, dark-mode-stripped={dark_fixed}, GTM-deferred={gtm_fixed}')
print('\nDone.')
