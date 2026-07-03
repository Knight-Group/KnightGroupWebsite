const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  for (const viewportWidth of [820, 1024, 1440]) {
    const page = await browser.newPage({ viewport: { width: viewportWidth, height: 900 } });
    await page.goto('http://127.0.0.1:8083/?v=form-call-fix-' + viewportWidth, { waitUntil: 'networkidle' });
    await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
    await page.waitForTimeout(2000);
    const sel = '.kg-hero-form-phone-row .kg-header-call';
    const before = await page.$eval(sel, (el) => {
      const r = el.getBoundingClientRect();
      const row = el.closest('.kg-hero-form-phone-row').getBoundingClientRect();
      return {
        transform: getComputedStyle(el).transform,
        enter: el.getAttribute('data-kg-enter'),
        delta: Math.abs(r.left + r.width / 2 - (row.left + row.width / 2))
      };
    });
    await page.hover(sel);
    await page.waitForTimeout(150);
    const hover = await page.$eval(sel, (el) => {
      const r = el.getBoundingClientRect();
      const row = el.closest('.kg-hero-form-phone-row').getBoundingClientRect();
      return {
        transform: getComputedStyle(el).transform,
        delta: Math.abs(r.left + r.width / 2 - (row.left + row.width / 2))
      };
    });
    console.log(viewportWidth, JSON.stringify({ before, hover, jump: Math.abs(hover.delta - before.delta).toFixed(2) }));
    await page.close();
  }
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
