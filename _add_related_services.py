import re, os

# Service page metadata: slug, label, and which other services to cross-link
# Each page gets 4 relevant cross-links
SERVICES = {
    'carpentry-framing.html': ('Carpentry & Framing', [
        ('general-repairs', 'General Repairs'),
        ('doors-windows', 'Doors & Windows'),
        ('home-renovations', 'Home Renovations'),
        ('painting-finishing', 'Painting & Finishing'),
    ]),
    'custom-projects.html': ('Custom Projects', [
        ('carpentry-framing', 'Carpentry & Framing'),
        ('home-renovations', 'Home Renovations'),
        ('painting-finishing', 'Painting & Finishing'),
        ('doors-windows', 'Doors & Windows'),
    ]),
    'doors-windows.html': ('Doors & Windows', [
        ('general-repairs', 'General Repairs'),
        ('carpentry-framing', 'Carpentry & Framing'),
        ('plumbing-services', 'Plumbing Services'),
        ('painting-finishing', 'Painting & Finishing'),
    ]),
    'electrical-work.html': ('Electrical Work', [
        ('general-repairs', 'General Repairs'),
        ('plumbing-services', 'Plumbing Services'),
        ('emergency-services', 'Emergency Services'),
        ('home-renovations', 'Home Renovations'),
    ]),
    'emergency-services.html': ('Emergency Services', [
        ('general-repairs', 'General Repairs'),
        ('plumbing-services', 'Plumbing Services'),
        ('electrical-work', 'Electrical Work'),
        ('handyman', 'Handyman Services'),
    ]),
    'general-repairs.html': ('General Repairs', [
        ('handyman', 'Handyman Services'),
        ('plumbing-services', 'Plumbing Services'),
        ('painting-finishing', 'Painting & Finishing'),
        ('doors-windows', 'Doors & Windows'),
    ]),
    'handyman.html': ('Handyman Services', [
        ('general-repairs', 'General Repairs'),
        ('home-renovations', 'Home Renovations'),
        ('painting-finishing', 'Painting & Finishing'),
        ('carpentry-framing', 'Carpentry & Framing'),
    ]),
    'home-renovations.html': ('Home Renovations', [
        ('carpentry-framing', 'Carpentry & Framing'),
        ('painting-finishing', 'Painting & Finishing'),
        ('electrical-work', 'Electrical Work'),
        ('plumbing-services', 'Plumbing Services'),
    ]),
    'painting-finishing.html': ('Painting & Finishing', [
        ('general-repairs', 'General Repairs'),
        ('home-renovations', 'Home Renovations'),
        ('carpentry-framing', 'Carpentry & Framing'),
        ('doors-windows', 'Doors & Windows'),
    ]),
    'plumbing-services.html': ('Plumbing Services', [
        ('general-repairs', 'General Repairs'),
        ('electrical-work', 'Electrical Work'),
        ('emergency-services', 'Emergency Services'),
        ('home-renovations', 'Home Renovations'),
    ]),
}

RELATED_CSS = """
    /* Related Services */
    .related-services {
        padding: 56px 0 48px;
        background: #f8f6f2;
    }
    .related-services h2 {
        text-align: center;
        font-size: clamp(1.4rem, 3vw, 1.9rem);
        color: #2c2c2c;
        margin-bottom: 32px;
    }
    .related-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    .related-card {
        background: #fff;
        border: 1px solid #e0ddd7;
        border-radius: 10px;
        padding: 22px 18px;
        text-align: center;
        text-decoration: none;
        color: #2c2c2c;
        font-weight: 600;
        font-size: 0.95rem;
        transition: box-shadow 0.2s, transform 0.2s;
        display: block;
    }
    .related-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        color: #800000;
    }
    @media (max-width: 700px) {
        .related-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 400px) {
        .related-grid { grid-template-columns: 1fr 1fr; }
    }
"""

RELATED_HTML_TPL = """
    <!-- Related Services -->
    <section class="related-services" aria-labelledby="related-heading">
        <div class="container">
            <h2 id="related-heading">Other Services We Offer</h2>
            <div class="related-grid">
{cards}
            </div>
        </div>
    </section>"""

INSERT_BEFORE = '    <!-- Footer Include -->'

def make_cards(links):
    cards = []
    for slug, label in links:
        cards.append(f'                <a href="/Services/{slug}" class="related-card">{label}</a>')
    return '\n'.join(cards)

os.chdir('Services')
fixed = 0
for filename, (current_label, links) in SERVICES.items():
    content = open(filename, encoding='utf-8').read()

    # Add CSS inside the last </style> before footer if not already present
    if 'related-services' not in content:
        # Insert CSS before closing </style> tag of the last <style> block
        last_style_close = content.rfind('</style>')
        if last_style_close == -1:
            print(f'  [skip-no-style] {filename}')
            continue
        content = content[:last_style_close] + RELATED_CSS + content[last_style_close:]

        # Insert HTML section before footer include
        cards_html = make_cards(links)
        related_block = RELATED_HTML_TPL.format(cards=cards_html)
        if INSERT_BEFORE in content:
            content = content.replace(INSERT_BEFORE, related_block + '\n\n' + INSERT_BEFORE)
            open(filename, 'w', encoding='utf-8').write(content)
            print(f'  [FIXED] {filename}')
            fixed += 1
        else:
            print(f'  [skip-no-anchor] {filename}')
    else:
        print(f'  [skip-exists] {filename}')

print(f'\nDone — {fixed} pages updated')
