const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  for (const [w, h] of [[1440, 900], [1366, 768], [1280, 800]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto('http://127.0.0.1:8083/?v=hero-faithworks-' + w, { waitUntil: 'networkidle' });
    await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 15000 });
    await page.waitForTimeout(2500);
    const d = await page.evaluate(() => {
      const copy = document.querySelector('.kg-hero-copy');
      const shell = document.querySelector('.kg-hero-form-shell');
      const card = document.querySelector('.kg-hero-form-card');
      const aside = document.querySelector('.kg-hero-proof-aside');
      const hero = document.querySelector('.kg-hero');
      const cr = copy.getBoundingClientRect();
      const sr = shell.getBoundingClientRect();
      const cardR = card.getBoundingClientRect();
      const heroR = hero.getBoundingClientRect();
      const asideStyle = aside ? getComputedStyle(aside).display : null;
      return {
        heroH: Math.round(heroR.height),
        copyH: Math.round(cr.height),
        shellH: Math.round(sr.height),
        cardH: Math.round(cardR.height),
        cardClip: card.scrollHeight > card.clientHeight + 2,
        cardScroll: card.scrollHeight,
        cardClient: card.clientHeight,
        textareaMin: getComputedStyle(document.getElementById('hero-message')).minHeight,
        asideDisplay: asideStyle,
        asideVisible: aside ? aside.getBoundingClientRect().width > 0 : false,
        gridLeft: Math.round(document.querySelector('.kg-hero__grid').getBoundingClientRect().left),
        shellBottom: Math.round(sr.bottom),
        heroBottom: Math.round(heroR.bottom),
        formInsideHero: sr.bottom <= heroR.bottom + 2
      };
    });
    console.log(w + 'x' + h, JSON.stringify(d));
    if (w === 1440) {
      await page.screenshot({ path: 'E:/All Client Websites/KnightGroupWebsite/scripts/screenshots/hero-faithworks-1440.png' });
    }
    await page.close();
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
