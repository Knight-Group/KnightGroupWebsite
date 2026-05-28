import glob

# Fix 1: index.html - add role="img" to all kg-stars elements
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'class="kg-stars" aria-label="5 stars">'
new = 'class="kg-stars" role="img" aria-label="5 stars">'
count = content.count(old)
content = content.replace(old, new)

# Fix 2: Change div.kg-review-name to h3.kg-review-name for article headings
content = content.replace('<div class="kg-review-name">', '<h3 class="kg-review-name">')
content = content.replace('</div>\n                                        <div class="kg-review-sub">', '</h3>\n                                        <div class="kg-review-sub">')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'index.html: replaced {count} kg-stars, fixed review name headings')

# Fix 3: galleries.html - h3 inside role=button → p.gallery-item-title; fix lightbox issues
with open('galleries.html', 'r', encoding='utf-8') as f:
    gcontent = f.read()

# Update CSS selector
gcontent = gcontent.replace('.gallery-item h3 {', '.gallery-item-title {')

# Change h3 inside gallery-item-info to p.gallery-item-title
import re
gcontent = re.sub(
    r'<div class="gallery-item-info">\s*<h3>([^<]+)</h3>',
    lambda m: '<div class="gallery-item-info"><p class="gallery-item-title">' + m.group(1) + '</p>',
    gcontent
)

# Fix empty src on lightbox img
gcontent = gcontent.replace('<img id="lightbox-img" src="" alt="">', '<img id="lightbox-img" alt="">')

# Fix empty lightbox h3 → p 
gcontent = gcontent.replace('<h3 id="lightbox-title"></h3>', '<p id="lightbox-title" class="lightbox-title-text"></p>')

# Update JS reference if it used h3 element (it uses getElementById, so tag change is fine)

with open('galleries.html', 'w', encoding='utf-8') as f:
    f.write(gcontent)

print('galleries.html: fixed h3-in-button, lightbox img src, lightbox title element')

# Fix 4: service-areas.html - add aria-label to section that lacks heading
with open('service-areas.html', 'r', encoding='utf-8') as f:
    sacontent = f.read()

sacontent = sacontent.replace('<section class="section">', '<section class="section" aria-label="Service area coverage details">')

with open('service-areas.html', 'w', encoding='utf-8') as f:
    f.write(sacontent)

print('service-areas.html: added aria-label to section without heading')

# Fix 5: Remove type="text/javascript" from all pages (W3C warning)
for filepath in glob.glob('*.html') + glob.glob('Services/*.html') + glob.glob('PolicyPages/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        fc = f.read()
    if 'type="text/javascript"' in fc:
        fc2 = fc.replace(' type="text/javascript"', '')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fc2)
        print(f'{filepath}: removed type="text/javascript"')

print('Done.')
