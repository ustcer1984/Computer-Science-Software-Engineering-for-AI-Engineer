import { chromium } from '/home/zhangzhou/.npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.mjs';
const URL = 'https://github.com/ustcer1984/Computer-Science-Software-Engineering-for-AI-Engineer/blob/main/courses/12-model-landscape/02-beyond-text/02-video-and-world-models.md';
const OUT = '/home/zhangzhou/Desktop/Projects/Computer-Science-Software-Engineering-for-AI-Engineer/temp-verify';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1100, height: 1400 }, deviceScaleFactor: 2 });
await page.goto(URL + '?t=' + Date.now(), { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(6000);
// Scroll the callout heading to the top of the viewport, then full-viewport screenshot.
await page.evaluate(() => {
  const hs = [...document.querySelectorAll('h3')];
  const t = hs.find(h => h.textContent.includes('Is this just a better optimizer'));
  if (t) t.scrollIntoView({ block: 'start' });
});
await page.waitForTimeout(1200);
await page.screenshot({ path: `${OUT}-1.png` });   // viewport = callout intro + first lever
// scroll down one viewport for the table + the rest
await page.evaluate(() => window.scrollBy(0, 1150));
await page.waitForTimeout(800);
await page.screenshot({ path: `${OUT}-2.png` });
await browser.close();
console.log('done');
