import glob, os

base = r'e:\KnightGroupWebsite'
files = glob.glob(base + r'\Services\*.html')

# The literal UTF-8 bytes for: content: '✓'
old_bytes = b"content: '\xe2\x9c\x93'"
# CSS Unicode escape (with trailing space per CSS spec): content: "\2713 "
new_bytes = b'content: "\\2713 "'

fixed = 0
for path in files:
    raw = open(path, 'rb').read()
    if old_bytes in raw:
        raw = raw.replace(old_bytes, new_bytes)
        open(path, 'wb').write(raw)
        print('FIXED:', os.path.basename(path))
        fixed += 1
    else:
        print('skipped:', os.path.basename(path))

# Also fix service-page.css (uses double-quotes already)
css_path = base + r'\CSS\service-page.css'
raw = open(css_path, 'rb').read()
old_css = b'content: "\xe2\x9c\x93"'
new_css = b'content: "\\2713 "'
if old_css in raw:
    raw = raw.replace(old_css, new_css)
    open(css_path, 'wb').write(raw)
    print('FIXED: service-page.css')
    fixed += 1

print('\nTotal fixed:', fixed)
