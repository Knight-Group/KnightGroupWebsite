const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const outDir = path.join(__dirname, 'screenshots', 'composites');
const previews = process.argv.slice(2);

async function capture() {
  if (!previews.length) {
    console.error('Usage: node capture-composite-preview.js <basename> [...]');
    process.exit(1);
  }

  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();

  for (const base of previews) {
    const jpg = path.join(__dirname, '..', 'GalleryImages', `${base}-social.jpg`);
    const webp = path.join(__dirname, '..', 'GalleryImages', `${base}.webp`);
    const src = fs.existsSync(jpg) ? jpg : webp;
    if (!fs.existsSync(src)) {
      console.error('Missing', src);
      continue;
    }

    const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body { margin:0; background:#111; display:flex; align-items:center; justify-content:center; min-height:100vh; }
  img { max-width:100vw; max-height:100vh; height:auto; width:auto; display:block; }
</style></head>
<body><img src="file:///${src.replace(/\\/g, '/')}" alt="${base}"></body></html>`;
    const htmlPath = path.join(outDir, `${base}-preview.html`);
    fs.writeFileSync(htmlPath, html);

    const page = await browser.newPage({ viewport: { width: 1672, height: 941 } });
    await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`, { waitUntil: 'load' });
    await page.waitForTimeout(400);
    const target = path.join(outDir, `${base}-verified.png`);
    await page.screenshot({ path: target, fullPage: false });
    console.log('Saved', target);
    await page.close();
  }

  await browser.close();
}

capture().catch((error) => {
  console.error(error);
  process.exit(1);
});
