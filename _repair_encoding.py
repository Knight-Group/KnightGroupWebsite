"""
Repair script: Fix broken UTF-8 sequences caused by naive byte replacement.

Problem: Previous encoding fix replaced all occurrences of bytes like 0x94, 0x97
with HTML entities, but these bytes also appear as valid 3rd bytes in UTF-8
multi-byte sequences (e.g., \xe2\x80\x94 = U+2014 em dash).

This script:
1. Repairs broken \xe2\x80 + entity patterns back to correct HTML entities
2. Also handles 2-byte sequences broken by naive replacement
"""

import glob
import re

# Map: when we see \xe2\x80 followed by one of these entities,
# we know the original UTF-8 byte and can determine the correct entity
BROKEN_SEQ_REPAIRS = {
    # \xe2\x80\x94 = U+2014 EM DASH (—)
    b'\xe2\x80&rdquo;': b'&mdash;',
    # \xe2\x80\x93 = U+2013 EN DASH (–)
    b'\xe2\x80&ldquo;': b'&ndash;',
    # \xe2\x80\x97 = U+2017 DOUBLE LOW LINE (rare, treat as em dash)
    b'\xe2\x80&mdash;': b'&mdash;',
    # \xe2\x80\x92 = U+2012 FIGURE DASH
    b'\xe2\x80&rsquo;': b'&ndash;',
    # \xe2\x80\x91 = U+2011 NON-BREAKING HYPHEN
    b'\xe2\x80&lsquo;': b'&#x2011;',
    # \xe2\x80\x96 = U+2016 DOUBLE VERTICAL LINE
    b'\xe2\x80&ndash;': b'&#x2016;',
    # \xe2\x80\x95 = U+2015 HORIZONTAL BAR
    b'\xe2\x80&bull;': b'&mdash;',
    # \xe2\x80\x85 = U+2005 FOUR-PER-EM SPACE
    b'\xe2\x80&hellip;': b'&hellip;',
    # E2 80 9D = U+201D RIGHT DOUBLE QUOTATION MARK (")
    # This would happen if \x9d was replaced, but we didn't replace 0x9D
    # \xe2\x80\x9c = U+201C LEFT DOUBLE QUOTATION MARK (") 
    # \xe2\x80\x99 = U+2019 RIGHT SINGLE QUOTATION MARK (')
    # \xe2\x80\x98 = U+2018 LEFT SINGLE QUOTATION MARK (')
}

# Also handle 2-byte sequences \xc2\x91 etc.
# \xc2 starts a 2-byte sequence for U+0080-U+00BF range
# But our replaced bytes (0x91-0x97) don't appear in \xc2 sequences typically
# (those would be \xc2\x91-\xc2\x9f for C1 control chars)

all_files = glob.glob('*.html') + glob.glob('Services/*.html') + glob.glob('PolicyPages/*.html')

fixed_files = []
for filepath in all_files:
    with open(filepath, 'rb') as f:
        content = f.read()
    
    original = content
    
    # Repair broken sequences
    for broken, repair in BROKEN_SEQ_REPAIRS.items():
        if broken in content:
            n = content.count(broken)
            content = content.replace(broken, repair)
            if content != original:
                print(f'  {filepath}: repaired {n}x {broken} -> {repair}')
    
    if content != original:
        with open(filepath, 'wb') as f:
            f.write(content)
        fixed_files.append(filepath)

print(f'\nRepaired {len(fixed_files)} files.')

# Now verify all files can be read as UTF-8
print('\nVerifying UTF-8 validity:')
errors = []
for filepath in all_files:
    with open(filepath, 'rb') as f:
        raw = f.read()
    # Strip BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        errors.append((filepath, str(e)))
        print(f'  STILL BROKEN: {filepath}: {e}')

if not errors:
    print('  All files are valid UTF-8!')
else:
    print(f'  {len(errors)} files still have issues.')
