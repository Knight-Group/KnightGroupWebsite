const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:8083/?v=hero-layout-debug2', { waitUntil: 'networkidle' });
  await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
  await page.waitForTimeout(2500);
  const shell = await page.$eval('.kg-hero-form-shell', (el) => {
    const cs = getComputedStyle(el);
    return {
      inline: el.getAttribute('style'),
      height: cs.height,
      minHeight: cs.minHeight,
      maxHeight: cs.maxHeight,
      overflow: cs.overflow,
      display: cs.display,
      flex: cs.flex
    };
  });
  const hero = await page.$eval('.kg-hero', (el) => {
    const cs = getComputedStyle(el);
    return { display: cs.display, width: cs.width, alignItems: cs.alignItems, justifyContent: cs.justifyContent };
  });
  const grid = await page.$eval('.kg-hero__grid', (el) => {
    const cs = getComputedStyle(el);
    return { width: cs.width, maxWidth: cs.maxWidth, flex: cs.flex, margin: cs.margin, alignSelf: cs.alignSelf };
  });
  console.log(JSON.stringify({ shell, hero, grid }, null, 2));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
