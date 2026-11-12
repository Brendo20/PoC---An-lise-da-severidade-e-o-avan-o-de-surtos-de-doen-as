const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const url = process.env.SRAG_PREVIEW_URL || 'http://127.0.0.1:8767/';
const assert = (value, message) => { if (!value) throw Error(message); };

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1500 } });
    const errors = [], posts = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => { if (request.method() === 'POST') posts.push(request.postDataJSON()); });
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => !document.querySelector('#sr-generate').disabled);
    await page.selectOption('#sr-a', 'SP'); await page.selectOption('#sr-b', 'MG');
    assert(posts.length === 0, 'filters automatically spent model quota');
    const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/reports') && response.request().method() === 'POST');
    await page.click('#sr-generate');
    const report = await (await responsePromise).json();
    await page.waitForFunction(() => document.querySelector('#sr-agent-status').textContent.includes('concluído'));
    assert(posts[0].territories.join(',') === 'SP,MG', 'wrong report scope');
    assert(posts[0].snapshot_id === report.snapshot_id, 'snapshot not pinned');
    const html = await page.request.get(url + `api/reports/${report.report_id}/html`);
    assert((await html.text()).split('<svg ').length - 1 === 2, 'report missing charts');
    const reportPage = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
    await reportPage.goto(url + `api/reports/${report.report_id}/html`);
    assert(await reportPage.locator('svg').count() === 2, 'HTML chart rendering');
    await reportPage.screenshot({ path: 'frontend/preview-agent-report.png', fullPage: true });
    await reportPage.close();
    assert(await page.locator('#sr-agent-result a').last().getAttribute('href') === `api/reports/${report.report_id}/html`, 'report link missing');
    await page.screenshot({ path: 'frontend/preview-agent.png', fullPage: true });
    await page.selectOption('#sr-a', 'RJ');
    assert(!await page.locator('#sr-agent-result').isVisible(), 'stale report after scope change');
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    await page.route('**/api/reports', async route => { await gate; await route.fulfill({ json: report }); });
    await page.click('#sr-generate');
    await page.selectOption('#sr-a', 'SP'); release();
    await page.waitForFunction(() => !document.querySelector('#sr-generate').disabled);
    assert(!await page.locator('#sr-agent-result').isVisible(), 'inflight result from old selection displayed');
    await page.unroute('**/api/reports');
    await page.route('**/api/reports', route => route.fulfill({ json: { ...report, status: 'partial', analysis: null } }));
    await page.click('#sr-generate');
    await page.waitForFunction(() => document.querySelector('#sr-agent-status').textContent.includes('parcial'));
    assert((await page.locator('#sr-agent-result').textContent()).includes('indisponível'), 'partial report not explicit');
    await page.setViewportSize({ width: 320, height: 900 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'mobile overflow');
    assert(errors.length === 0, 'JS errors: ' + errors.join(','));
    const result = { status: 'passed', backend: 'fixture_not_live_groq_or_postgres',
      explicitGeneration: true, selectedTerritories: true, pinnedSnapshot: true,
      twoReportCharts: true, staleResponsesDiscarded: true, partialState: true, mobileOverflow: false, errors };
    fs.writeFileSync('reports/frontend-agent.json', JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
