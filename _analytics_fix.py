"""
Apply optimal third-party script loading patterns to ALL pages:
- GTM: requestIdleCallback with 5s timeout (more time for idle)
- Clarity: setTimeout 6000 (already done for index, apply to all)

Also apply to pages that have the old window.addEventListener('load') pattern.
"""
import re, os, glob

ROOT = 'e:\\KnightGroupWebsite'
os.chdir(ROOT)

def read(p): return open(p, encoding='utf-8').read()
def write(p, c): open(p, 'w', encoding='utf-8').write(c)

# Old GTM load-on-window-load pattern (used by most pages)
OLD_GTM_BLOCK = """    window.addEventListener('load', function() {
        var s = document.createElement('script');
        s.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG';
        s.async = true;
        document.head.appendChild(s);
        window.dataLayer.push({'gtm.start': new Date().getTime(), event: 'gtm.js'});
    });"""

# New GTM: requestIdleCallback with 5s timeout
NEW_GTM_BLOCK = """    var _gtmLoaded = false;
    function _loadGTM() {
        if (_gtmLoaded) return;
        _gtmLoaded = true;
        var s = document.createElement('script');
        s.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-MNHVDBHG';
        s.async = true;
        document.head.appendChild(s);
        window.dataLayer.push({'gtm.start': new Date().getTime(), event: 'gtm.js'});
    }
    if ('requestIdleCallback' in window) {
        requestIdleCallback(_loadGTM, { timeout: 5000 });
    } else {
        setTimeout(_loadGTM, 5000);
    }"""

# Old Clarity timeout values
OLD_CLARITY_TIMEOUT = '}, 2500);'
NEW_CLARITY_TIMEOUT = '}, 6000);'

# The existing index.html pattern (4s timeout) also needs updating to 5s
OLD_GTM_4S = '        requestIdleCallback(_loadGTM, { timeout: 4000 });\n    } else {\n        setTimeout(_loadGTM, 4000);'
NEW_GTM_5S = '        requestIdleCallback(_loadGTM, { timeout: 5000 });\n    } else {\n        setTimeout(_loadGTM, 5000);'

# Collect all live HTML pages
all_html = (
    glob.glob('*.html') +
    glob.glob('Services/*.html') +
    glob.glob('PolicyPages/*.html')
)
EXCLUDE = {'page-template.html', 'socialCards.html', 'head-gtm.html',
           '_carpentry_corrupted.html', '_handyman_corrupted.html',
           '_fix_round2.py', 'payment-policy-test.html'}
live_pages = [p for p in all_html if os.path.basename(p) not in EXCLUDE
              and 'handcraftedfurniture' not in p and 'programming' not in p]

print(f'Processing {len(live_pages)} pages...\n')
gtm_fixed = clarity_fixed = 0

for p in sorted(live_pages):
    orig = read(p)
    content = orig
    
    # Fix GTM loading
    if OLD_GTM_BLOCK in content:
        content = content.replace(OLD_GTM_BLOCK, NEW_GTM_BLOCK)
        gtm_fixed += 1
    
    # Update 4s timeout to 5s (index.html already updated)
    if OLD_GTM_4S in content:
        content = content.replace(OLD_GTM_4S, NEW_GTM_5S)
    
    # Fix Clarity timeout
    if OLD_CLARITY_TIMEOUT in content:
        content = content.replace(OLD_CLARITY_TIMEOUT, NEW_CLARITY_TIMEOUT)
        clarity_fixed += 1
    
    if content != orig:
        write(p, content)
        print(f'  [FIXED] {p}')

print(f'\nSummary: GTM-deferred={gtm_fixed}, Clarity-delay-extended={clarity_fixed}')
print('Done.')
