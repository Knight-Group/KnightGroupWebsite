"""
_cls_skeleton_fix.py
--------------------
Adds a sticky skeleton header inside every #header-include div so the 
exact header height is reserved from the very first paint (frame 1).
This eliminates CLS caused by the async header injection via includes.js.

The skeleton has:
  - height: 68px + border-bottom: 3px = 71px total (real header = 71px)
  - bg: #fff, border maroon, box-shadow — visually matches real header
  - position: sticky; top: 0; z-index: 1000
  - aria-hidden so screen readers skip it
  - removed when includes.js replaces innerHTML (seamless 71px -> 71px)
"""
import re
import os
import glob

SKELETON_HTML = '''<div aria-hidden="true" id="header-skeleton" style="height:68px;background:#fff;border-bottom:3px solid #800000;box-shadow:0 2px 14px rgba(0,0,0,.08);position:sticky;top:0;z-index:1000;width:100%;box-sizing:content-box;"></div>'''

# Match empty or already-skeleton-only #header-include
EMPTY_INCLUDE = re.compile(
    r'(<div\s+id=["\']header-include["\']>)\s*(</div>)',
    re.IGNORECASE
)

ALREADY_SKELETON = '<div aria-hidden="true" id="header-skeleton"'

ROOT = r'e:\KnightGroupWebsite'
HTML_FILES = (
    glob.glob(os.path.join(ROOT, '*.html')) +
    glob.glob(os.path.join(ROOT, 'Services', '*.html')) +
    glob.glob(os.path.join(ROOT, 'PolicyPages', '*.html'))
)

fixed = 0
skipped = 0

for path in sorted(HTML_FILES):
    fname = os.path.relpath(path, ROOT)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip non-content files
    if 'header-include' not in content:
        print(f'  [SKIP-NoTarget] {fname}')
        skipped += 1
        continue

    # Skip if already has the skeleton
    if ALREADY_SKELETON in content:
        print(f'  [SKIP-AlreadyDone] {fname}')
        skipped += 1
        continue

    new_content = EMPTY_INCLUDE.sub(
        r'\1' + SKELETON_HTML + r'\2',
        content,
        count=1
    )

    if new_content == content:
        print(f'  [SKIP-PatternNoMatch] {fname}')
        skipped += 1
        continue

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  [FIXED] {fname}')
    fixed += 1

print(f'\nDone. Fixed: {fixed}, Skipped: {skipped}')
