const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const outDir = path.join(__dirname, 'screenshots');
const url = 'http://127.0.0.1:8083/?v=20260624-hero-mobile-verified3';
const widths = [390, 820, 1200];

async function capture() {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();

  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForSelector('.kg-hero.kg-hero-panels-ready', { timeout: 10000 });
    await page.waitForTimeout(1200);
    const target = path.join(outDir, `hero-${width}-verified.png`);
    await page.screenshot({ path: target, fullPage: false });
    console.log('Saved', target);
    await page.close();
  }

  await browser.close();
}

capture().catch(function (error) {
  console.error(error);
  process.exit(1);
});
