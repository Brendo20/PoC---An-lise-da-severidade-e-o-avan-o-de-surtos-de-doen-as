// SRAG_PLAYWRIGHT_MODULE may point to a preinstalled Playwright package.
const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const url = process.env.SRAG_PREVIEW_URL || 'http://127.0.0.1:8765/';

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
    const errors = [], remote = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => { if (!request.url().startsWith(url)) remote.push(request.url()); });
    const assert = (condition, message) => { if (!condition) throw Error(message); };
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.locator('#sr-app').waitFor({ state: 'visible' });
    assert(await page.locator('#sr-map path').count() === 27, 'missing map paths');
    assert((await page.locator('#sr-detail').innerText()).includes('48.866'), 'national count mismatch');
    assert((await page.locator('#sr-growth').innerText()).includes('-11,8'), 'national growth mismatch');
    assert((await page.locator('#sr-fatal').innerText()).includes('12,1'), 'national fatality mismatch');
    await page.locator('#sr-a').selectOption('SP');
    await page.locator('#sr-b').selectOption('MG');
    assert(await page.locator('#sr-context').innerText() === 'São Paulo × Minas Gerais', 'comparison title');
    assert((await page.locator('#sr-detail').innerText()).includes('12.312'), 'SP count mismatch');
    assert((await page.locator('#sr-detail').innerText()).includes('4.021'), 'MG count mismatch');
    const growthBefore = await page.locator('#sr-growth').innerText();
    await page.locator('#sr-report').click();
    assert((await page.locator('#sr-report-body').innerText()).includes('12.312'), 'summary data mismatch');
    assert(await page.locator('#sr-report').getAttribute('aria-expanded') === 'true', 'summary expansion');
    await page.locator('#sr-level').selectOption('region');
    await page.locator('#sr-a').selectOption('Norte');
    await page.locator('#sr-b').selectOption('Sudeste');
    assert(await page.locator('#sr-map path.a').count() === 7, 'Norte map selection');
    assert(await page.locator('#sr-map path.b').count() === 4, 'Sudeste map selection');
    assert((await page.locator('#sr-report-body').innerText()).includes('Norte × Sudeste'), 'stale report');
    await page.screenshot({ path: 'frontend/preview-desktop.png', fullPage: true });
    await page.locator('#sr-level').selectOption('state');
    await page.locator('#sr-a').selectOption('AC');
    assert((await page.locator('#sr-daily-note').innerText()).includes('omitidos'), 'small daily cells not marked');
    const suppressed = await page.locator('#sr-daily-table td').allTextContents();
    assert(suppressed.some(text => text.includes('suprimido')), 'suppression missing in accessible table');
    for (const width of [320, 360, 768]) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(120);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'overflow at ' + width);
    }
    await page.setViewportSize({ width: 360, height: 900 });
    await page.locator('#sr-b').selectOption('SP');
    await page.screenshot({ path: 'frontend/preview-mobile.png', fullPage: true });
    await page.locator('#sr-reset').click();
    assert(await page.locator('#sr-a').inputValue() === 'Brasil', 'reset main');
    assert(await page.locator('#sr-b').inputValue() === '', 'reset comparison');
    await page.locator('#sr-map path[data-uf="SP"]').click();
    assert(await page.locator('#sr-a').inputValue() === 'SP', 'map pointer selection');
    await page.route('**/data/snapshot.json', route => route.fulfill({ status: 404, body: 'not found' }));
    await page.reload({ waitUntil: 'networkidle' });
    assert(await page.locator('[role="alert"]').isVisible(), 'missing load failure state');
    assert(!await page.locator('#sr-app').isVisible(), 'stale dashboard visible after failure');
    assert(errors.length === 0, 'JavaScript error: ' + errors.join('; '));
    assert(remote.length === 0, 'external runtime requests: ' + remote.join('; '));
    const results = { status: 'passed', map: 27, comparison: ['SP x MG', 'Norte x Sudeste'],
      validatedNationalCases: 48866, widths: [320, 360, 768, 1100],
      suppression: true, failureState: true, pageErrors: errors, remoteRequests: remote };
    fs.writeFileSync('reports/frontend-smoke.json', JSON.stringify(results, null, 2));
    console.log(JSON.stringify(results));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
