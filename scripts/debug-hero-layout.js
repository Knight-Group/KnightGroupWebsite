const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:8083/?v=hero-layout-debug', { waitUntil: 'networkidle' });
  await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
  await page.waitForTimeout(2500);

  const data = await page.evaluate(() => {
    const copy = document.querySelector('.kg-hero-copy');
    const shell = document.querySelector('.kg-hero-form-shell');
    const card = document.querySelector('.kg-hero-form-card');
    const grid = document.querySelector('.kg-hero__grid');
    const cr = (el) => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        left: Math.round(r.left),
        top: Math.round(r.top),
        width: Math.round(r.width),
        height: Math.round(r.height),
        heightStyle: el.style.height || null,
        computedHeight: cs.height,
        alignSelf: cs.alignSelf,
        justifySelf: cs.justifySelf
      };
    };
    const gridCs = grid ? getComputedStyle(grid) : null;
    return {
      grid: cr(grid),
      gridAlign: gridCs ? gridCs.alignItems : null,
      gridCols: gridCs ? gridCs.gridTemplateColumns : null,
      copy: cr(copy),
      shell: cr(shell),
      card: cr(card),
      heightDiff: shell && copy ? Math.round(copy.getBoundingClientRect().height - shell.getBoundingClientRect().height) : null
    };
  });

  console.log(JSON.stringify(data, null, 2));
  await page.screenshot({ path: 'E:/All Client Websites/KnightGroupWebsite/scripts/screenshots/hero-layout-1440.png' });
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
