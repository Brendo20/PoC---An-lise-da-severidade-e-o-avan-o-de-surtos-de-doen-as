// Integration checks: every dashboard surface must reflect the same territory selection.
const fs = require('node:fs');
const { chromium } = require(process.env.SRAG_PLAYWRIGHT_MODULE || 'playwright');
const url = process.env.SRAG_PREVIEW_URL || 'http://127.0.0.1:8765/';
const data = JSON.parse(fs.readFileSync('frontend/data/snapshot.json', 'utf8'));
const config = [
  ['growth', 'growth', 1], ['fatal', 'fatality', 1],
  ['icu', 'icu_admission', 2], ['vaccine', 'flu_vaccination_cases', 2],
];
const name = id => data.states.find(item => item.id === id)?.name || id;
const pct = (metric, digits, key = '') => metric.status === 'available'
  ? new Intl.NumberFormat('pt-BR', { maximumFractionDigits: digits }).format(metric.value) + '%'
  : metric.status === 'suppressed' ? 'Suprimido'
    : key === 'growth' && metric.reason === 'zero_denominator' ? 'Sem casos' : 'Indisponível';
const count = point => point.status === 'available' ? new Intl.NumberFormat('pt-BR').format(point.value)
  : point.status === 'suppressed' ? '< 5 · suprimido' : 'Indisponível';
const assert = (ok, message) => { if (!ok) throw Error(message); };

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.locator('#sr-app').waitFor({ state: 'visible' });
    await page.locator('#sr-report').click();
    let checks = 0;
    async function check(a, b = '', level = 'state') {
      const ids = [a, ...(b ? [b] : [])];
      const state = await page.locator('#srag-design').evaluate(node => ({ ...node.dataset }));
      assert(state.territory === a && state.comparison === b && state.level === level, 'state mismatch');
      assert(await page.locator('#sr-a').inputValue() === a, 'main menu mismatch');
      assert(await page.locator('#sr-b').inputValue() === b, 'comparison menu mismatch');
      assert(await page.locator('#sr-context').innerText() === ids.map(name).join(' × '), 'context mismatch');
      assert(await page.locator('#sr-b').isDisabled() === (a === 'Brasil'), 'comparison enable mismatch');
      assert((await page.locator('#sr-report-body').textContent()).includes('Resumo de ' + ids.map(name).join(' × ')), 'stale summary context');
      const mainNames = await page.locator('.sr-main-name').allTextContents();
      assert(mainNames.length === 4 && mainNames.every(value => value === name(a)), 'stale card labels');
      for (const [id, key, digits] of config) {
        assert(await page.locator('#sr-' + id).innerText() === pct(data.territories[a].metrics[key], digits, key), 'card mismatch: ' + a + ' / ' + key);
        const comparison = await page.locator('#sr-' + id + '-b').textContent();
        if (b) assert(comparison.startsWith(name(b) + ': ' + pct(data.territories[b].metrics[key], digits, key)), 'comparison card mismatch: ' + key);
        else assert(comparison === '', 'stale comparison card');
        const notes = await page.locator('#sr-' + id + '-note').textContent();
        const item = data.territories[a].metrics[key];
        if (item.status === 'available') {
          assert(notes.includes(new Intl.NumberFormat('pt-BR').format(item.numerator)), 'numerator mismatch');
          assert(notes.includes(new Intl.NumberFormat('pt-BR').format(item.denominator)), 'denominator mismatch');
        } else assert(notes.includes('suprimido') || notes.includes('não calculável') || notes.includes('cobertura'), 'missing unavailable reason');
      }
      for (const territory of ids) {
        const quality = await page.locator('#sr-scope-quality section[data-territory="' + territory + '"]').textContent();
        for (const [, key, digits] of config) assert(quality.includes(pct(data.territories[territory].metrics[key], digits, key)), 'stale scope quality');
      }
      assert(await page.locator('#sr-scope-quality section').count() === ids.length, 'extra quality scope');
      const expectedPaths = territory => territory === 'Brasil' ? 0 : level === 'state' ? 1 : data.states.filter(item => item.region === territory).length;
      assert(await page.locator('#sr-map path.a').count() === expectedPaths(a), 'main map mismatch');
      assert(await page.locator('#sr-map path.b').count() === (b ? expectedPaths(b) : 0), 'comparison map mismatch');
      for (const kind of ['daily', 'monthly']) {
        const columns = await page.locator('#sr-' + kind + '-table thead th').allTextContents();
        assert(JSON.stringify(columns) === JSON.stringify(['Período', ...ids.map(name)]), 'table columns mismatch');
        const cells = await page.locator('#sr-' + kind + '-table tbody td').allTextContents();
        const expected = data.territories[a][kind].flatMap((_, i) => ids.map(id => count(data.territories[id][kind][i])));
        assert(JSON.stringify(cells) === JSON.stringify(expected), 'table data mismatch: ' + kind);
        for (let i = 0; i < ids.length; i++) {
          const circles = await page.locator('#sr-' + kind + ' circle' + (i ? '.second' : ':not(.second)')).count();
          assert(circles === data.territories[ids[i]][kind].filter(point => point.status === 'available').length, 'chart marks mismatch');
        }
        const accessible = await page.locator('#sr-' + kind + ' svg').getAttribute('aria-label');
        assert(ids.every(id => accessible.includes(name(id))), 'stale chart accessible label');
      }
      const legends = await page.locator('.sr-chart-legend').allTextContents();
      assert(legends.every(text => ids.every(id => text.includes(name(id)))), 'stale legends');
      checks++;
    }
    await check('Brasil');
    assert(await page.locator('#sr-icu').textContent() === '36,93%', 'national ICU finding');
    assert(await page.locator('#sr-vaccine').textContent() === '32,08%', 'national vaccination finding');
    for (const territory of data.states.map(item => item.id)) {
      await page.locator('#sr-a').selectOption(territory);
      await check(territory);
    }
    await page.locator('#sr-a').selectOption('SP');
    await page.locator('#sr-b').selectOption('MG');
    await check('SP', 'MG');
    await page.locator('#sr-target-b').click();
    await page.locator('#sr-map path[data-uf="PR"]').click();
    await check('SP', 'PR');
    await page.locator('#sr-target-a').click();
    await page.locator('#sr-map path[data-uf="MG"]').click();
    await check('MG', 'PR');
    await page.locator('#sr-a').selectOption('PR');
    await check('PR'); // main equals comparison: clear comparison everywhere
    await page.locator('#sr-compare').click();
    const automatic = await page.locator('#sr-b').inputValue();
    await check('PR', automatic);
    await page.locator('#sr-compare').click();
    await check('PR');
    await page.locator('#sr-level').selectOption('region');
    await check('Brasil', '', 'region');
    for (const region of data.regions) {
      await page.locator('#sr-a').selectOption(region);
      await check(region, '', 'region');
    }
    await page.locator('#sr-a').selectOption('Norte');
    await page.locator('#sr-b').selectOption('Sudeste');
    await check('Norte', 'Sudeste', 'region');
    await page.locator('#sr-target-b').click();
    await page.locator('#sr-map path[data-uf="PR"]').click();
    await check('Norte', 'Sul', 'region');
    await page.locator('#sr-map path[data-uf="AM"]').click();
    await check('Norte', 'Sul', 'region'); // self comparison is rejected
    await page.locator('#sr-reset').click();
    await check('Brasil', '', 'region');
    await page.locator('#sr-level').selectOption('state');
    await page.locator('#sr-a').selectOption('SP');
    await page.locator('#sr-b').selectOption('MG');
    await page.screenshot({ path: 'frontend/preview-desktop.png', fullPage: true });
    for (const width of [320, 360, 768]) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(150);
      await check('SP', 'MG');
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'overflow at ' + width);
    }
    await page.setViewportSize({ width: 360, height: 900 });
    await page.screenshot({ path: 'frontend/preview-mobile.png', fullPage: true });
    assert(errors.length === 0, 'browser errors: ' + errors.join('; '));
    const result = { status: 'passed', synchronizedSelections: checks, states: 27, regions: 5,
      surfaces: ['cards', 'denominators', 'comparison', 'menus', 'map', 'charts', 'tables', 'summary', 'quality', 'legends'],
      mapTargets: ['main', 'comparison'], widths: [320, 360, 768, 1100], browserErrors: errors };
    fs.writeFileSync('reports/frontend-filters.json', JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
