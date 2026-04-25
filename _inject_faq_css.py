import glob
import os

FAQ_CSS = """
    /* === FAQ SECTION === */
    .faq-section {
        background: #f4f6f9;
        padding: 80px 0;
        border-top: 1px solid #e2e8f0;
    }
    .faq-section .container {
        max-width: 820px;
    }
    .faq-section h2 {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #800000;
        text-align: center;
        margin-bottom: 48px;
    }
    .faq-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .faq-item {
        background: #fff;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        overflow: hidden;
        transition: box-shadow 0.2s ease;
    }
    .faq-item:hover {
        box-shadow: 0 4px 14px rgba(128,0,0,0.10);
    }
    .faq-item[open] {
        border-color: #800000;
        box-shadow: 0 4px 16px rgba(128,0,0,0.12);
    }
    .faq-item summary {
        list-style: none;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 20px 24px;
        cursor: pointer;
        font-weight: 600;
        font-size: 1.05rem;
        color: #1a1a2e;
        user-select: none;
        transition: background 0.15s ease, color 0.15s ease;
    }
    .faq-item summary::-webkit-details-marker { display: none; }
    .faq-item summary::after {
        content: "+";
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #800000;
        color: #fff;
        font-size: 1.2rem;
        line-height: 28px;
        text-align: center;
        font-weight: 400;
        transition: transform 0.25s ease, background 0.2s ease;
    }
    .faq-item[open] > summary {
        background: #faf5f5;
        color: #800000;
        border-bottom: 1px solid #f0e0e0;
    }
    .faq-item[open] > summary::after {
        content: "\\2212";
    }
    .faq-item > p {
        padding: 20px 24px 22px;
        font-size: 1rem;
        line-height: 1.75;
        color: #444;
        margin: 0;
    }
    body.dark-mode .faq-section {
        background: #111620;
        border-top-color: #2d3748;
    }
    body.dark-mode .faq-item {
        background: #1a1f2e;
        border-color: #2d3748;
    }
    body.dark-mode .faq-item[open] {
        border-color: #ff6b6b;
    }
    body.dark-mode .faq-item summary {
        color: #f0f0f0;
    }
    body.dark-mode .faq-item summary::after {
        background: #c0392b;
    }
    body.dark-mode .faq-item[open] > summary {
        background: #1e1015;
        color: #ff6b6b;
        border-bottom-color: #3d1a1a;
    }
    body.dark-mode .faq-item > p {
        color: #d0d0d0;
    }
    body.dark-mode .faq-section h2 {
        color: #ff6b6b;
    }
    @media (max-width: 600px) {
        .faq-section { padding: 56px 0; }
        .faq-section h2 { font-size: 1.7rem; }
        .faq-item summary { font-size: 0.97rem; padding: 16px 18px; }
        .faq-item > p { padding: 16px 18px 18px; }
    }
"""

svc = r'e:\KnightGroupWebsite\Services'
files = glob.glob(svc + r'\*.html')
changed = []

for path in files:
    content = open(path, 'r', encoding='utf-8').read()
    if '/* === FAQ SECTION ===' in content:
        print(f'SKIP (already has FAQ CSS): {os.path.basename(path)}')
        continue
    new_content = content.replace('    </style>', FAQ_CSS + '    </style>', 1)
    if new_content == content:
        print(f'NO </style> found in: {os.path.basename(path)}')
        continue
    open(path, 'w', encoding='utf-8').write(new_content)
    changed.append(os.path.basename(path))

print('Updated:', changed)
