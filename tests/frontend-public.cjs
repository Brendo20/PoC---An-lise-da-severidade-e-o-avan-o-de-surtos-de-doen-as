/* Revisão somente leitura da demonstração real; nenhuma geração LLM é permitida. */
const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const base = 'https://poc-srag.estacaolab.com.br/';
const reportId = process.env.SRAG_REVIEW_REPORT_ID || 'd55a99bf5d54456e9c89442fcc25e9e6';
const assert = (value, message) => { if (!value) throw Error(message); };

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1500 } });
    const errors = [], writes = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/*', route => {
      if (!['GET', 'HEAD'].includes(route.request().method())) {
        writes.push(route.request().method()); return route.abort();
      }
      return route.continue();
    });
    const response = await page.goto(base, { waitUntil: 'networkidle' });
    assert(response.status() === 200, 'public dashboard HTTP');
    await page.locator('#sr-app').waitFor({ state: 'visible' });
    assert(await page.locator('#srag-design').getAttribute('data-data-source') === 'api', 'not API mode');
    const data = await (await page.request.get(base + 'api/dashboard')).json();
    assert(data.territories.Brasil.metrics.cases.value === 48866, 'national cases');
    await page.selectOption('#sr-a', 'SP'); await page.selectOption('#sr-b', 'MG');
    assert(await page.locator('#srag-design').getAttribute('data-comparison') === 'MG', 'comparison');
    await page.screenshot({ path: 'frontend/preview-public-dashboard.png', fullPage: true });
    await page.setViewportSize({ width: 360, height: 900 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'dashboard mobile overflow');
    for (const path of ['.env', 'data/snapshot.json', 'src/srag/database.py']) {
      assert((await page.request.get(base + path)).status() === 404, 'private path exposed: ' + path);
    }
    const report = await (await page.request.get(base + 'api/reports/' + reportId)).json();
    assert(report.status === 'complete' && report.analysis, 'accepted report missing');
    assert(report.snapshot_id === data.snapshot_id, 'snapshot mismatch');
    await page.setViewportSize({ width: 1100, height: 1500 });
    const html = await page.goto(base + 'api/reports/' + reportId + '/html', { waitUntil: 'networkidle' });
    assert(html.status() === 200, 'public report HTTP');
    assert(await page.locator('svg').count() === 2, 'two charts missing');
    await page.screenshot({ path: 'frontend/preview-public-report.png', fullPage: true });
    await page.setViewportSize({ width: 360, height: 900 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'report mobile overflow');
    assert(!errors.length && !writes.length, 'browser error or attempted write');
    const result = { status: 'passed', origin: base, reportId, source: 'real_hml_read_only',
      snapshot_id: data.snapshot_id, cases: 48866, news: report.news.articles.length,
      charts: 2, widths: [360, 1100], privatePathsBlocked: true,
      modelRequestsTriggered: 0, browserErrors: errors };
    fs.writeFileSync('reports/public-review.json', JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
    console.log(JSON.stringify({ historical: report.analysis.historical_commentary,
      current: report.analysis.current_commentary, citations: report.analysis.cited_news_ids }, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
