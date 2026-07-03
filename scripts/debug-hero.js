const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const w of [390, 820]) {
    const page = await browser.newPage({ viewport: { width: w, height: 844 } });
    await page.goto('http://127.0.0.1:8083/?v=20260624-hero-mobile-verified2', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    const info = await page.evaluate(() => {
      const hero = document.querySelector('.kg-hero');
      const stage = document.querySelector('.kg-hero-portrait-stage');
      const img = document.querySelector('.kg-hero-cutout');
      const lead = document.querySelector('.kg-hero__lead');
      const actions = document.querySelector('.kg-hero__actions');
      const cs = (el) => el ? getComputedStyle(el) : null;
      const rect = (el) => el ? el.getBoundingClientRect() : null;
      return {
        heroReady: hero?.classList.contains('kg-hero-panels-ready'),
        heroMinH: cs(hero)?.minHeight,
        heroH: rect(hero)?.height,
        heroDisplay: cs(hero)?.display,
        heroAlign: cs(hero)?.alignItems,
        stagePos: cs(stage)?.position,
        stageH: rect(stage)?.height,
        stageTop: rect(stage)?.top,
        imgOpacity: cs(img)?.opacity,
        imgDisplay: cs(img)?.display,
        imgH: rect(img)?.height,
        imgVis: img ? (rect(img).height > 0 && cs(img).opacity !== '0') : false,
        leadBottom: rect(lead)?.bottom,
        actionsTop: rect(actions)?.top,
        gap: rect(actions)?.top - rect(lead)?.bottom,
        imgTop: rect(img)?.top,
        order: Array.from(document.querySelector('.kg-hero-copy')?.children || []).map(el => el.className)
      };
    });
    console.log('WIDTH', w, JSON.stringify(info, null, 2));
  }
  await browser.close();
})();
