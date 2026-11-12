// Run with SRAG_PLAYWRIGHT_MODULE pointing to the installed Playwright package.
const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const fragment = fs.readFileSync('design/srag-wireframe.html', 'utf8');
    await page.setContent('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>body{margin:20px;color-scheme:light}[hidden]{display:none!important}</style></head><body>' + fragment + '</body></html>', { waitUntil: 'networkidle' });
    await page.locator('#sr-map path').first().waitFor({ timeout: 30000 });
    const assert = (condition, message) => { if (!condition) throw Error(message); };
    assert(await page.locator('#sr-map path').count() === 27, '27 UF paths expected');
    await page.locator('#sr-a').selectOption('SP');
    await page.locator('#sr-b').selectOption('MG');
    assert(await page.locator('#sr-context').innerText() === 'São Paulo × Minas Gerais', 'state comparison');
    assert(await page.locator('#sr-map path.a').count() === 1, 'main state selection');
    assert(await page.locator('#sr-map path.b').count() === 1, 'comparison state selection');
    await page.locator('#sr-level').selectOption('region');
    await page.locator('#sr-a').selectOption('Norte');
    await page.locator('#sr-b').selectOption('Sudeste');
    assert(await page.locator('#sr-map path.a').count() === 7, 'Norte geometry');
    assert(await page.locator('#sr-map path.b').count() === 4, 'Sudeste geometry');
    await page.locator('#sr-report').click();
    assert(await page.locator('#sr-report-body').isVisible(), 'report preview');
    await page.screenshot({ path: 'design/desktop-preview.png', fullPage: true });
    await page.setViewportSize({ width: 360, height: 800 });
    await page.waitForTimeout(150);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    assert(!overflow, 'mobile overflow');
    await page.screenshot({ path: 'design/mobile-preview.png', fullPage: true });
    await page.locator('#sr-reset').click();
    assert(await page.locator('#sr-a').inputValue() === 'Brasil', 'reset main');
    assert(await page.locator('#sr-b').inputValue() === '', 'reset comparison');
    await page.locator('#sr-level').selectOption('state');
    await page.locator('#sr-map path[data-uf="SP"]').click();
    assert(await page.locator('#sr-a').inputValue() === 'SP', 'map click');
    assert(errors.length === 0, 'browser errors: ' + errors.join('; '));
    console.log(JSON.stringify({ paths: 27, states: 'SP x MG passed', regions: 'Norte x Sudeste passed', report: 'passed', mobileOverflow: overflow, reset: 'passed', mapClick: 'passed', pageErrors: errors }));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
