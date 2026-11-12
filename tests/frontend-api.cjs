const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const url = process.env.SRAG_PREVIEW_URL || 'http://127.0.0.1:8767/';
const assert = (ok, message) => { if (!ok) throw Error(message); };

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
    const requests = [], errors = [];
    page.on('request', request => requests.push(request.url()));
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.locator('#sr-app').waitFor({ state: 'visible' });
    assert(await page.locator('#srag-design').getAttribute('data-data-source') === 'api', 'data source not API');
    const reference = await page.locator('#sr-reference').textContent();
    assert(reference.includes('última carga em') && reference.includes('09:45'), 'load date not shown');
    assert((await page.locator('#sr-audit-body').textContent()).includes('Carga PostgreSQL realizada em'), 'stale load status');
    assert(requests.some(request => request.endsWith('/api/dashboard')), 'API was not fetched');
    assert(!requests.some(request => request.includes('/data/snapshot.json')), 'disk snapshot requested');
    assert((await page.request.get(url + 'data/snapshot.json')).status() === 404, 'disk snapshot exposed');
    await page.screenshot({ path: 'frontend/preview-api.png', fullPage: true });
    await page.route('**/api/dashboard', route => route.fulfill({ status: 503, body: '{}' }));
    await page.reload({ waitUntil: 'networkidle' });
    assert(await page.locator('[role="alert"]').isVisible(), 'API failure not shown');
    assert(!await page.locator('#sr-app').isVisible(), 'stale content retained after failed load');
    assert(!requests.some(request => request.includes('/data/snapshot.json')), 'silent fallback to disk');
    assert(errors.length === 0, 'JS errors');
    const result = { status: 'passed', backend: 'in_memory_fixture_not_postgres',
      source: 'api', loadTimestamp: true, diskSnapshotNotRequested: true,
      diskSnapshotBlocked: true, fallbackOnFailure: false, errors };
    fs.writeFileSync('reports/frontend-api.json', JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
