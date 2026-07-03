const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  for (const [w, h] of [[1440, 900], [1366, 768], [1024, 768]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto('http://127.0.0.1:8083/?v=hero-form-height-' + w, { waitUntil: 'networkidle' });
    await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
    await page.waitForTimeout(2500);
    const d = await page.evaluate(() => {
      const copy = document.querySelector('.kg-hero-copy');
      const shell = document.querySelector('.kg-hero-form-shell');
      const grid = document.querySelector('.kg-hero__grid');
      const gr = grid.getBoundingClientRect();
      const cr = copy.getBoundingClientRect();
      const sr = shell.getBoundingClientRect();
      return {
        gridLeft: Math.round(gr.left),
        gridWidth: Math.round(gr.width),
        heightDiff: Math.round(cr.height - sr.height),
        shellHeight: Math.round(sr.height),
        copyHeight: Math.round(cr.height)
      };
    });
    console.log(w + 'x' + h, JSON.stringify(d));
    await page.close();
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
