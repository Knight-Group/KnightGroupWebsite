with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print('kg-stars with role=img:', c.count('role="img" aria-label="5 stars"'))
print('kg-review-name as h3:', c.count('<h3 class="kg-review-name">'))
print('kg-review-name as div (bad):', c.count('<div class="kg-review-name">'))
print('job carousel role=region:', c.count('role="region" aria-label="Previous Knight Group jobs carousel"'))
print('reviews section aria-label:', c.count('aria-label="Customer Reviews"'))

with open('galleries.html', 'r', encoding='utf-8') as f:
    g = f.read()

print('gallery-item-title p:', g.count('class="gallery-item-title"'))
print('lightbox img src empty (bad):', 'src=""' in g)
print('lightbox title as p:', '<p id="lightbox-title"' in g)
print('lightbox title as h3 (bad):', '<h3 id="lightbox-title"' in g)

with open('service-areas.html', 'r', encoding='utf-8') as f:
    s = f.read()
print('service-areas section aria-label:', 'aria-label="Service area coverage details"' in s)
