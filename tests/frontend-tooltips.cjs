const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const url = process.env.SRAG_PREVIEW_URL || 'http://127.0.0.1:8765/';
const data = JSON.parse(fs.readFileSync('frontend/data/snapshot.json', 'utf8'));
const assert = (ok, message) => { if (!ok) throw Error(message); };

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1200 } });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.locator('#sr-app').waitFor({ state: 'visible' });
    assert(await page.locator('h1').textContent() === 'PoC - Análise da severidade e o avanço de surtos de doenças', 'heading');
    const weights = await page.locator('.metric > .small:first-child').evaluateAll(nodes => nodes.map(node => getComputedStyle(node).fontWeight));
    assert(weights.length === 4 && weights.every(value => Number(value) >= 700), 'card titles are not bold');
    await page.locator('#sr-a').selectOption('RR');
    assert(await page.locator('#sr-growth').textContent() === 'Sem casos', 'zero denominator label');
    assert((await page.locator('#sr-growth-note').textContent()).includes('7 dias anteriores'), 'missing period clarification');
    await page.locator('#sr-a').selectOption('AC');
    assert(await page.locator('#sr-growth').textContent() === 'Suprimido', 'small counts must not be called zero');
    await page.locator('#sr-reset').click();
    for (const kind of ['daily', 'monthly']) {
      const hit = page.locator('#sr-' + kind + ' .chart-hit');
      const box = await hit.boundingBox();
      await hit.hover({ position: { x: box.width - 1, y: box.height / 2 } });
      const tooltip = page.locator('#sr-' + kind + '-tooltip');
      assert(await tooltip.isVisible(), 'hover tooltip missing: ' + kind);
      const point = data.territories.Brasil[kind].at(-1);
      const value = new Intl.NumberFormat('pt-BR').format(point.value);
      assert((await tooltip.textContent()).includes('Brasil: ' + value + ' casos'), 'tooltip data mismatch');
      if (kind === 'monthly') assert((await tooltip.textContent()).includes('parcial'), 'partial month missing');
      await page.locator('#sr-' + kind + ' svg').focus();
      await page.keyboard.press('Home');
      assert((await tooltip.textContent()).includes(new Intl.NumberFormat('pt-BR').format(data.territories.Brasil[kind][0].value)), 'keyboard tooltip mismatch');
      await page.keyboard.press('End'); await page.keyboard.press('Escape');
      assert(!await tooltip.isVisible(), 'escape does not close tooltip');
    }
    await page.locator('#sr-a').selectOption('AC');
    await page.locator('#sr-b').selectOption('SP');
    await page.locator('#sr-daily svg').focus();
    const index = data.territories.AC.daily.findIndex(point => point.status === 'suppressed');
    assert(index >= 0, 'no suppressed fixture');
    await page.keyboard.press('Home');
    for (let i = 0; i < index; i++) await page.keyboard.press('ArrowRight');
    const tooltip = await page.locator('#sr-daily-tooltip').textContent();
    assert(tooltip.includes('Acre: < 5 · suprimido') && tooltip.includes('São Paulo:'), 'comparison/suppression tooltip');
    await page.screenshot({ path: 'frontend/preview-tooltip.png', fullPage: true });
    await page.setViewportSize({ width: 320, height: 900 });
    await page.waitForTimeout(150);
    await page.locator('#sr-monthly svg').focus(); await page.keyboard.press('End');
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'mobile overflow');
    const tipBox = await page.locator('#sr-monthly-tooltip').boundingBox();
    assert(tipBox.x >= 0 && tipBox.x + tipBox.width <= 320, 'tooltip overflows mobile');
    assert(errors.length === 0, 'JS errors: ' + errors.join('; '));
    const result = { status: 'passed', heading: true, boldTitles: 4, zeroLabel: 'Sem casos',
      suppressedLabel: 'Suprimido', charts: ['daily', 'monthly'], interactions: ['hover', 'keyboard', 'escape'],
      comparison: true, partialMonth: true, suppressedValues: true, mobileWidth: 320, errors };
    fs.writeFileSync('reports/frontend-tooltips.json', JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
