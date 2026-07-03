const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1024, height: 768 } });
  await page.goto('http://127.0.0.1:8083/?v=debug-form-call', { waitUntil: 'networkidle' });
  await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
  await page.waitForTimeout(2000);
  const sel = '.kg-hero-form-phone-row .kg-header-call';
  const before = await page.$eval(sel, (el) => getComputedStyle(el).transform);
  const boxBefore = await page.$eval(sel, (el) => {
    const r = el.getBoundingClientRect();
    const row = el.closest('.kg-hero-form-phone-row').getBoundingClientRect();
    return {
      callCenter: r.left + r.width / 2,
      rowCenter: row.left + row.width / 2,
      delta: Math.abs(r.left + r.width / 2 - (row.left + row.width / 2)),
      enter: el.getAttribute('data-kg-enter'),
      visible: el.classList.contains('is-visible')
    };
  });
  await page.hover(sel);
  await page.waitForTimeout(200);
  const during = await page.$eval(sel, (el) => getComputedStyle(el).transform);
  const boxDuring = await page.$eval(sel, (el) => {
    const r = el.getBoundingClientRect();
    const row = el.closest('.kg-hero-form-phone-row').getBoundingClientRect();
    return {
      callCenter: r.left + r.width / 2,
      rowCenter: row.left + row.width / 2,
      delta: Math.abs(r.left + r.width / 2 - (row.left + row.width / 2))
    };
  });
  console.log(JSON.stringify({ before, during, boxBefore, boxDuring }, null, 2));
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
