/* Snapshot local de agregações; métricas são calculadas em Python, não no navegador. */
'use strict';

(() => {
  const root = document.getElementById('srag-design');
  const $ = selector => root.querySelector(selector);
  const state = { level: 'state', a: 'Brasil', b: '', target: 'a' };
  const dataSource = document.querySelector('meta[name="srag-data-source"]')?.content || 'local';
  const int = new Intl.NumberFormat('pt-BR');
  const decimal = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
  const dateFormat = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' });
  const shortDate = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', timeZone: 'UTC' });
  let data;
  let geometry;
  let resizeTimer;
  let agentConfigured = false;
  let generating = false;
  let scopeVersion = 0;
  const displayDate = text => dateFormat.format(new Date(text + 'T00:00:00Z'));
  const displayTimestamp = text => new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Sao_Paulo',
  }).format(new Date(text));
  const name = id => data.states.find(item => item.id === id)?.name || id;
  const selected = () => [state.a, ...(state.b ? [state.b] : [])];
  const metric = (id, key) => data.territories[id].metrics[key];
  const pct = (item, digits = 1, key = '') => item.status === 'available'
    ? `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: digits }).format(item.value)}%`
    : item.status === 'suppressed' ? 'Suprimido'
      : key === 'growth' && item.reason === 'zero_denominator' ? 'Sem casos' : 'Indisponível';
  const indicators = [
    { key: 'growth', id: 'growth', label: 'Crescimento em 7 dias', digits: 1 },
    { key: 'fatality', id: 'fatal', label: 'Letalidade entre desfechos conhecidos', digits: 1 },
    { key: 'icu_admission', id: 'icu', label: 'Internação em UTI entre casos com informação', digits: 2 },
    { key: 'flu_vaccination_cases', id: 'vaccine', label: 'Vacinação contra gripe entre casos com informação', digits: 2 },
  ];
  const count = item => item.status === 'available' ? int.format(item.value) : item.status === 'suppressed' ? '< 5 · suprimido' : 'Indisponível';
  const reason = item => item.status === 'suppressed' ? 'Categoria pequena · valor suprimido' : ({
    zero_denominator: 'Denominador zero · não calculável',
    outside_coverage: 'Período fora da cobertura declarada',
    missing_bed_source: 'Fonte de leitos indisponível',
    missing_population_source: 'Fonte populacional indisponível',
  }[item.reason] || 'Indisponível');

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function options() {
    return state.level === 'state'
      ? data.states.map(item => [item.id, item.name]).sort((a, b) => a[1].localeCompare(b[1], 'pt-BR'))
      : data.regions.map(region => [region, region]);
  }

  function populate() {
    $('#sr-level').value = state.level;
    $('#sr-a').replaceChildren(new Option('Brasil', 'Brasil'), ...options().map(([id, label]) => new Option(label, id)));
    $('#sr-a').value = state.a;
    $('#sr-b').replaceChildren(new Option('Sem comparação', ''), ...options().filter(([id]) => id !== state.a).map(([id, label]) => new Option(label, id)));
    $('#sr-b').value = state.b;
    $('#sr-b').disabled = state.a === 'Brasil';
  }

  function updateFilters(action, value) {
    const previous = JSON.stringify(selected());
    const valid = id => options().some(([key]) => key === id);
    if (action === 'level') {
      if (!['state', 'region'].includes(value)) return;
      Object.assign(state, { level: value, a: 'Brasil', b: '', target: 'a' });
    } else if (action === 'reset') {
      Object.assign(state, { a: 'Brasil', b: '', target: 'a' });
    } else if (action === 'a') {
      if (value !== 'Brasil' && !valid(value)) return;
      state.a = value;
      if (value === 'Brasil' || value === state.b) state.b = '';
      state.target = 'a';
    } else if (action === 'b') {
      if (state.a === 'Brasil' || (value && (!valid(value) || value === state.a))) return;
      state.b = value;
      state.target = value ? 'b' : 'a';
    } else if (action === 'target') {
      if (!['a', 'b'].includes(value) || (value === 'b' && state.a === 'Brasil')) return;
      state.target = value;
    } else if (action === 'map') {
      if (!valid(value)) return;
      if (state.target === 'b') {
        if (value === state.a) {
          $('#sr-map-status').textContent = 'Escolha um território diferente do principal para comparar.';
          return;
        }
        state.b = value;
      } else {
        state.a = value;
        if (value === state.b) state.b = '';
      }
    }
    populate();
    render();
    if (previous !== JSON.stringify(selected())) {
      scopeVersion++;
      $('#sr-agent-result').hidden = true;
      $('#sr-agent-result').replaceChildren();
      $('#sr-agent-status').textContent = generating ? 'Concluindo a solicitação anterior. Gere um novo relatório para este recorte.' : agentConfigured ? 'Recorte alterado. Gere um relatório para a seleção atual.' : 'Agente indisponível nesta prévia.';
    }
  }

  function renderMap() {
    const svg = $('#sr-map');
    const width = Math.max(230, svg.clientWidth);
    const height = svg.clientHeight;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    const projection = d3.geoMercator().fitExtent([[10, 12], [width - 10, height - 12]], geometry);
    const path = d3.geoPath(projection);
    svg.replaceChildren();
    geometry.features.forEach(feature => {
      const item = data.states.find(item => item.code === String(feature.properties.codarea));
      if (!item) throw Error('Malha geográfica sem correspondência de UF');
      const territory = state.level === 'state' ? item.id : item.region;
      const polygon = document.createElementNS(svg.namespaceURI, 'path');
      polygon.setAttribute('d', path(feature));
      polygon.setAttribute('class', territory === state.a ? 'a' : territory === state.b ? 'b' : '');
      polygon.dataset.uf = item.id;
      const title = document.createElementNS(svg.namespaceURI, 'title');
      title.textContent = `${item.name} · selecionar ${name(territory)}`;
      polygon.append(title);
      polygon.addEventListener('click', () => updateFilters('map', territory));
      svg.append(polygon);
      if (width > 360 && !['DF', 'SE', 'AL', 'PB', 'RN', 'ES', 'RJ'].includes(item.id)) {
        const [x, y] = path.centroid(feature);
        const text = document.createElementNS(svg.namespaceURI, 'text');
        text.setAttribute('x', x); text.setAttribute('y', y);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('class', territory === state.a || territory === state.b ? 'selected' : '');
        text.textContent = item.id;
        svg.append(text);
      }
    });
    $('#sr-map-mode').textContent = state.level === 'state' ? 'Estados' : 'Regiões';
    $('#sr-target-a').setAttribute('aria-pressed', String(state.target === 'a'));
    $('#sr-target-b').setAttribute('aria-pressed', String(state.target === 'b'));
    $('#sr-target-b').disabled = state.a === 'Brasil';
    $('#sr-map-status').textContent = state.target === 'b'
      ? 'O próximo clique altera o território de comparação.' : 'O próximo clique altera o território principal.';
  }

  function rateNote(item) {
    return item.status === 'available'
      ? `${int.format(item.numerator)} / ${int.format(item.denominator)} · sem informação: ${decimal.format(item.unknown_percent)}%`
      : reason(item);
  }

  function metricNote(item, key) {
    if (key === 'growth' && item.reason === 'zero_denominator') {
      return 'Sem casos nos 7 dias anteriores · crescimento não calculável';
    }
    return key === 'growth' && item.status === 'available'
      ? `${int.format(item.numerator)} casos / ${int.format(item.denominator)} nos 7 dias anteriores`
      : rateNote(item);
  }

  function renderMetrics() {
    indicators.forEach(({ key, id, digits }) => {
      const item = metric(state.a, key);
      $(`#sr-${id}`).textContent = pct(item, digits, key);
      $(`#sr-${id}`).classList.toggle('status-value', item.status !== 'available');
      $(`#sr-${id}-note`).textContent = metricNote(item, key);
      const compared = state.b ? metric(state.b, key) : null;
      $(`#sr-${id}-b`).textContent = compared
        ? `${name(state.b)}: ${pct(compared, digits, key)} · ${metricNote(compared, key)}` : '';
    });
    root.querySelectorAll('.sr-main-name').forEach(node => { node.textContent = name(state.a); });
    $('#sr-detail-title').textContent = state.b ? 'Comparação territorial' : name(state.a);
    const detail = $('#sr-detail');
    detail.replaceChildren();
    selected().forEach((id, i) => {
      const section = element('div', 'summary');
      const heading = element('div', 'territory');
      heading.append(element('span', `dot${i ? ' second' : ''}`), element('span', '', name(id)));
      section.append(heading);
      for (const [label, value] of [
        ['Casos no período', count(metric(id, 'cases'))],
        ['Letalidade observada', pct(metric(id, 'fatality'))],
        ['Crescimento em 7 dias', pct(metric(id, 'growth'), 1, 'growth')],
        ['Internação em UTI entre casos', pct(metric(id, 'icu_admission'), 2)],
        ['Vacinação contra gripe entre casos', pct(metric(id, 'flu_vaccination_cases'), 2)],
      ]) {
        const row = element('div', 'row');
        row.append(element('span', 'small', label), element('strong', '', value));
        section.append(row);
      }
      detail.append(section);
    });
    $('#sr-compare').textContent = state.b ? 'Remover comparação' : 'Adicionar comparação';
    $('#sr-compare').disabled = state.a === 'Brasil';
  }

  function renderChart(kind) {
    const container = $(`#sr-${kind}`);
    const width = Math.max(230, container.clientWidth), height = 170;
    const margin = { left: 44, right: 12, top: 12, bottom: 26 };
    const series = selected().map(id => ({ id, points: data.territories[id][kind] }));
    const visible = series.flatMap(series => series.points.filter(point => point.status === 'available').map(point => point.value));
    const max = Math.max(1, ...visible);
    const yMax = d3.scaleLinear().domain([0, max]).nice(3).domain()[1];
    const x = d3.scaleLinear().domain([0, series[0].points.length - 1]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([0, yMax]).range([height - margin.bottom, margin.top]);
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('chart'); svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.setAttribute('role', 'img');
    svg.setAttribute('tabindex', '0');
    svg.setAttribute('aria-label', `Número de casos ${kind === 'daily' ? 'por dia' : 'por mês'} para ${selected().map(name).join(' e ')}. Lacunas são valores suprimidos ou sem cobertura. Valores acessíveis na tabela abaixo.`);
    const add = (tag, attrs, text) => {
      const node = document.createElementNS(svg.namespaceURI, tag);
      Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
      if (text !== undefined) node.textContent = text;
      svg.append(node); return node;
    };
    for (const tick of y.ticks(3)) {
      add('line', { x1: margin.left, x2: width - margin.right, y1: y(tick), y2: y(tick) });
      add('text', { x: margin.left - 5, y: y(tick) + 4, 'text-anchor': 'end' }, int.format(tick));
    }
    series.forEach((item, j) => {
      const line = d3.line().defined(point => point.status === 'available').x((point, i) => x(i)).y(point => y(point.value));
      add('path', { d: line(item.points) || '', class: j ? 'second' : '' });
      item.points.forEach((point, i) => {
        if (point.status !== 'available') return;
        const circle = add('circle', { cx: x(i), cy: y(point.value), r: 2.7, class: `point${j ? ' second' : ''}` });
        const title = document.createElementNS(svg.namespaceURI, 'title');
        title.textContent = `${name(item.id)} · ${displayDate(point.date)}: ${int.format(point.value)} casos${point.partial ? ' · mês parcial' : ''}`;
        circle.append(title);
      });
    });
    const points = series[0].points;
    const label = point => kind === 'daily' ? shortDate.format(new Date(point.date + 'T00:00:00Z')) : new Intl.DateTimeFormat('pt-BR', { month: 'short', timeZone: 'UTC' }).format(new Date(point.date + 'T00:00:00Z')) + (point.partial ? '*' : '');
    add('text', { x: margin.left, y: height - 5 }, label(points[0]));
    add('text', { x: width - margin.right, y: height - 5, 'text-anchor': 'end' }, label(points.at(-1)));
    const tooltip = element('div', 'chart-tooltip');
    tooltip.id = `sr-${kind}-tooltip`;
    tooltip.setAttribute('role', 'tooltip');
    tooltip.hidden = true;
    svg.setAttribute('aria-describedby', tooltip.id);
    const cursor = add('line', { x1: margin.left, x2: margin.left, y1: margin.top,
      y2: height - margin.bottom, class: 'chart-cursor', visibility: 'hidden' });
    const hit = add('rect', { x: margin.left, y: margin.top,
      width: width - margin.left - margin.right, height: height - margin.top - margin.bottom,
      class: 'chart-hit' });
    let activeIndex = 0;
    function showPoint(index) {
      activeIndex = Math.max(0, Math.min(points.length - 1, index));
      const point = points[activeIndex];
      const heading = kind === 'daily' ? displayDate(point.date)
        : new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })
          .format(new Date(point.date + 'T00:00:00Z')) + (point.partial ? ' · parcial' : '');
      tooltip.replaceChildren(element('strong', '', heading));
      series.forEach(item => {
        const value = item.points[activeIndex];
        const row = element('p', '', `${name(item.id)}: ${count(value)}${value.status === 'available' ? ' casos' : ''}`);
        tooltip.append(row);
      });
      cursor.setAttribute('x1', x(activeIndex)); cursor.setAttribute('x2', x(activeIndex));
      cursor.setAttribute('visibility', 'visible'); tooltip.hidden = false;
    }
    function hidePoint() { tooltip.hidden = true; cursor.setAttribute('visibility', 'hidden'); }
    function pointerPoint(event) {
      const local = svg.createSVGPoint(); local.x = event.clientX; local.y = event.clientY;
      const transformed = local.matrixTransform(svg.getScreenCTM().inverse());
      showPoint(Math.round(x.invert(transformed.x)));
    }
    hit.addEventListener('pointermove', pointerPoint);
    hit.addEventListener('pointerdown', pointerPoint);
    svg.addEventListener('pointerleave', hidePoint);
    svg.addEventListener('focus', () => showPoint(activeIndex));
    svg.addEventListener('blur', hidePoint);
    svg.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End', 'Escape'].includes(event.key)) return;
      event.preventDefault();
      if (event.key === 'Escape') hidePoint();
      else showPoint(event.key === 'Home' ? 0 : event.key === 'End' ? points.length - 1
        : activeIndex + (event.key === 'ArrowRight' ? 1 : -1));
    });
    container.classList.add('chart-container');
    container.replaceChildren(svg, tooltip);
    const unavailable = series.reduce((sum, item) => sum + item.points.filter(point => point.status !== 'available').length, 0);
    $(`#sr-${kind}-note`).textContent = `${unavailable ? unavailable + ' pontos omitidos. ' : ''}Lacunas ≠ zero · valores na tabela${kind === 'monthly' ? ' · * mês parcial' : ''}`;
    renderTable(kind, series);
  }

  function renderTable(kind, series) {
    const table = element('table');
    const caption = element('caption', 'a11y', `Casos ${kind === 'daily' ? 'diários' : 'mensais'} por território`);
    const head = element('thead'); const row = element('tr');
    ['Período', ...series.map(item => name(item.id))].forEach(text => { const th = element('th', '', text); th.scope = 'col'; row.append(th); });
    head.append(row); table.append(caption, head);
    const body = element('tbody');
    series[0].points.forEach((point, i) => {
      const row = element('tr');
      const heading = element('th', '', displayDate(point.date) + (point.partial ? ' (parcial)' : ''));
      heading.scope = 'row'; row.append(heading);
      series.forEach(item => { row.append(element('td', '', count(item.points[i]))); });
      body.append(row);
    });
    table.append(body); $(`#sr-${kind}-table`).replaceChildren(table);
  }

  function renderReport() {
    const body = $('#sr-report-body'); body.replaceChildren();
    body.append(element('h3', '', `Resumo de ${selected().map(name).join(' × ')}`));
    selected().forEach(id => {
      const cases = metric(id, 'cases');
      const total = cases.status === 'available' ? `${int.format(cases.value)} registros` : 'contagem indisponível ou suprimida';
      body.append(element('h3', '', `${name(id)}: ${total} no período`));
      indicators.forEach(({ key, label, digits }) => {
        const item = metric(id, key);
        body.append(element('p', '', `${label}: ${pct(item, digits, key)}. ${metricNote(item, key)}.`));
      });
    });
    body.append(element('p', 'small', 'Resumo calculado a partir das agregações, sem uso de LLM. Comparações absolutas não medem risco populacional. Mortalidade populacional, ocupação real de UTI e cobertura vacinal populacional não são calculáveis exclusivamente com este CSV. Letalidade entre os casos é apresentada com definição própria.'));
    body.append(element('p', 'small', 'Notícias e explicações do agente serão integradas em etapa posterior, com separação entre contexto histórico e atual.'));
  }

  function renderAudit() {
    const audit = $('#sr-audit-body');
    const generated = displayTimestamp(data.generated_at);
    const load = data.database_load;
    audit.replaceChildren();
    const link = element('a', '', 'Fonte: Open DATASUS · SIVEP-Gripe 2019');
    link.href = data.source.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; audit.append(link);
    [
      `Snapshot gerado em ${generated} (São Paulo). ${load?.status === 'loaded'
        ? 'Carga PostgreSQL realizada em ' + displayTimestamp(load.loaded_at) + ' (São Paulo).'
        : 'Prévia local: sem consulta ao banco nesta execução.'}`,
      `Origem: ${data.source.filename}. SHA-256: ${data.source.sha256}.`,
      `Referência analítica: ${displayDate(data.reference)}. Cobertura declarada: ${displayDate(data.coverage.start)} a ${displayDate(data.coverage.end)}. Cobertura declarada não garante completude das notificações.`,
      `Arquivo original: ${int.format(data.audit.input_rows)} linhas; janela nacional: ${int.format(data.audit.cases_in_window)} registros. Estes totais descrevem a origem, não o filtro territorial. Casos sem UF reconhecida no arquivo: ${int.format(data.audit.issues.unknown_residence_uf || 0)}, incluídos no Brasil.`,
      'Data dos casos: início dos sintomas. Território: residência. Desfechos: estado disponível na extração. Uma notificação não equivale necessariamente a uma pessoa única.',
      'Letalidade = óbitos por SRAG / desfechos conhecidos × 100. Óbitos por outras causas entram no denominador, sem entrar no numerador. Mortalidade populacional exige outra definição e fonte.',
      'Crescimento = (casos nos últimos 7 dias / casos nos 7 anteriores − 1) × 100. Denominador zero não produz uma taxa.',
      'Internação em UTI = UTI=1 / UTI em {1,2} × 100, entre casos notificados com informação conhecida. Não há filtro adicional HOSPITAL=1: os denominadores são os mesmos do estudo do recorte e não de uma coorte estritamente hospitalizada. Não mede capacidade ou ocupação operacional.',
      'Vacinação contra gripe entre casos = VACINA=1 / VACINA em {1,2} × 100. Respostas vazias e ignoradas são desconhecidas, não não vacinadas. Datas posteriores aos sintomas impedem presumir proteção prévia; esta proporção descreve o campo declarado, não eficácia vacinal ou cobertura populacional.',
      'Contagens de 1 a 4 são suprimidas; zeros permanecem zeros. Supressão primária não elimina inferências entre agregados sobrepostos. Dados restritos à validação local; não publicar este snapshot sem revisão adicional.',
      `Versão das métricas: ${data.metric_version}. Snapshot: ${data.snapshot_id}.`,
    ].forEach(text => audit.append(element('p', '', text)));
    const quality = element('section', 'scope-quality'); quality.id = 'sr-scope-quality';
    quality.append(element('h3', '', `Qualidade do recorte: ${selected().map(name).join(' × ')}`));
    selected().forEach(id => {
      const scope = element('section'); scope.dataset.territory = id;
      scope.append(element('h3', '', name(id)), element('p', '', `Casos no período: ${count(metric(id, 'cases'))}.`));
      indicators.forEach(({ key, label, digits }) => {
        scope.append(element('p', '', `${label}: ${pct(metric(id, key), digits, key)} · ${metricNote(metric(id, key), key)}.`));
      });
      quality.append(scope);
    });
    audit.prepend(quality);
    $('#sr-build').textContent = `Snapshot ${data.snapshot_id.split('-').slice(0, 2).join('-')} · métricas v${data.metric_version}`;
  }

  function render() {
    $('#sr-context').textContent = selected().map(name).join(' × ');
    renderMetrics(); renderMap(); renderChart('daily'); renderChart('monthly'); renderReport(); renderAudit();
    root.dataset.territory = state.a;
    root.dataset.comparison = state.b;
    root.dataset.level = state.level;
    root.querySelectorAll('.sr-chart-legend').forEach(node => {
      node.replaceChildren();
      selected().forEach((id, i) => {
        const label = element('span'); label.append(element('span', `dot${i ? ' second' : ''}`), document.createTextNode(` ${name(id)}${i ? ' · tracejado' : ''}`)); node.append(label);
      });
    });
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw Error(`Falha ao carregar ${path} (HTTP ${response.status})`);
    return response.json();
  }

  async function initAgent() {
    if (dataSource === 'api') {
      try { agentConfigured = (await loadJson('api/agent/status')).configured === true; }
      catch { agentConfigured = false; }
    }
    $('#sr-generate').disabled = !agentConfigured;
    $('#sr-agent-status').textContent = agentConfigured ? 'Pronto para gerar o relatório da seleção atual.' : 'Agente não configurado. Disponível no ambiente com provedor de IA habilitado.';
  }

  async function generateReport() {
    if (generating || !agentConfigured) return;
    const version = scopeVersion;
    generating = true;
    $('#sr-generate').disabled = true;
    $('#sr-generate').textContent = 'Gerando…';
    $('#sr-agent-result').hidden = true;
    $('#sr-agent-status').textContent = 'Consultando indicadores, séries e notícias. Aguarde a validação do relatório.';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 180000);
    try {
      const response = await fetch('api/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ territories: selected(), snapshot_id: data.snapshot_id }), signal: controller.signal });
      const result = await response.json();
      if (!response.ok) {
        const message = response.status === 429 ? 'Aguarde um minuto antes de gerar outro relatório.' : response.status === 409 ? 'A carga mudou. Atualize o dashboard antes de gerar o relatório.' : 'Não foi possível gerar o relatório. Confira o serviço e tente novamente.';
        throw Error(message);
      }
      if (version !== scopeVersion) return;
      const panel = $('#sr-agent-result'); panel.replaceChildren();
      panel.append(element('h3', '', selected().map(name).join(' × ')), element('p', 'small', `Gerado em ${displayTimestamp(result.generated_at)} (Brasília)${result.cached ? ' · relatório reutilizado' : ''}`));
      panel.append(element('h3', '', 'Análise histórica'), element('p', '', result.analysis?.historical_commentary || 'Comentário da IA indisponível ou rejeitado. Consulte os indicadores e gráficos no relatório.'));
      panel.append(element('h3', '', 'Notícias atuais · contexto separado'));
      if (result.analysis?.current_commentary) panel.append(element('p', '', result.analysis.current_commentary));
      if (!result.news.articles.length) panel.append(element('p', '', 'Nenhuma notícia recente verificada disponível nesta consulta.'));
      for (const article of result.news.articles) {
        let url; try { url = new URL(article.url); } catch { continue; }
        if (url.protocol !== 'https:' || url.username || url.password) continue;
        const paragraph = element('p'); const link = element('a', '', article.title);
        link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
        paragraph.append(link, element('span', 'small', ` · ${article.source} · ${displayTimestamp(article.published_at)}`)); panel.append(paragraph);
      }
      if (/^[a-f0-9]{32}$/.test(result.report_id)) {
        const link = element('a', '', 'Abrir relatório completo com os dois gráficos e auditoria');
        link.href = `api/reports/${result.report_id}/html`; link.target = '_blank'; link.rel = 'noopener noreferrer'; panel.append(link);
      }
      panel.hidden = false;
      $('#sr-agent-status').textContent = result.status === 'complete' ? 'Relatório concluído e validado.' : 'Relatório parcial: comentário da IA ou notícias indisponíveis. Indicadores preservados.';
    } catch (error) {
      if (version === scopeVersion) $('#sr-agent-status').textContent = error.name === 'AbortError' ? 'Tempo de espera excedido. A solicitação pode ainda estar em andamento.' : error.message;
    } finally {
      clearTimeout(timeout); generating = false;
      $('#sr-generate').disabled = !agentConfigured; $('#sr-generate').textContent = 'Gerar relatório';
      if (version !== scopeVersion) $('#sr-agent-status').textContent = 'Recorte alterado. Gere um novo relatório para a seleção atual.';
    }
  }

  async function init() {
    try {
      if (!['local', 'api'].includes(dataSource)) throw Error('Fonte de dados não reconhecida.');
      // Modo definido no HTML pelo servidor. Não há fallback de API para arquivo antigo.
      const endpoint = dataSource === 'api' ? 'api/dashboard' : 'data/snapshot.json';
      [data, geometry] = await Promise.all([loadJson(endpoint), loadJson('assets/brazil-states.geojson')]);
      if (data.schema_version !== '1.0.0' || !data.territories?.Brasil || geometry.features?.length !== 27 || !window.d3) throw Error('Dados ou biblioteca incompatíveis. Gere novamente o snapshot e confira os arquivos locais.');
      if (dataSource === 'api' && (data.database_load?.status !== 'loaded' || !data.database_load.loaded_at)) {
        throw Error('A API não informou uma carga válida.');
      }
      for (const feature of geometry.features) {
        const polygons = feature.geometry.type === 'Polygon' ? [feature.geometry.coordinates] : feature.geometry.coordinates;
        for (const coordinates of polygons) if (d3.geoArea({ type: 'Polygon', coordinates }) > 2 * Math.PI) coordinates.forEach(ring => ring.reverse());
      }
      const loadLabel = dataSource === 'api'
        ? 'última carga em ' + displayTimestamp(data.database_load.loaded_at) + ' (Brasília)'
        : 'prévia local';
      $('#sr-reference').textContent = `Base histórica · referência em ${displayDate(data.reference)} · ${loadLabel}`;
      root.querySelector('.top .badge').textContent = dataSource === 'api' ? 'Dados reais · HML' : 'Dados reais · uso local';
      root.dataset.dataSource = dataSource;
      $('#sr-period').textContent = `Período comum · ${displayDate(data.window_start)} a ${displayDate(data.reference)}`;
      const daily = data.territories.Brasil.daily;
      $('#sr-daily-period').textContent = `${displayDate(daily[0].date)} — ${displayDate(data.reference)} · registros reais`;
      $('#sr-monthly-period').textContent = `12 meses até ${displayDate(data.reference)} · mês final parcial`;
      $('#sr-app').hidden = false; $('#sr-loading').hidden = true;
      populate(); render();
      $('#sr-generate').addEventListener('click', generateReport);
      initAgent();
      $('#sr-level').addEventListener('change', event => updateFilters('level', event.target.value));
      $('#sr-a').addEventListener('change', event => updateFilters('a', event.target.value));
      $('#sr-b').addEventListener('change', event => updateFilters('b', event.target.value));
      $('#sr-reset').addEventListener('click', () => updateFilters('reset'));
      $('#sr-target-a').addEventListener('click', () => updateFilters('target', 'a'));
      $('#sr-target-b').addEventListener('click', () => updateFilters('target', 'b'));
      $('#sr-compare').addEventListener('click', () => updateFilters('b', state.b ? '' : options().find(([id]) => id !== state.a)[0]));
      $('#sr-report').addEventListener('click', () => { const panel = $('#sr-report-body'); panel.hidden = !panel.hidden; $('#sr-report').setAttribute('aria-expanded', String(!panel.hidden)); $('#sr-report').textContent = panel.hidden ? 'Resumo dos dados' : 'Recolher resumo'; });
      let width = root.clientWidth;
      new ResizeObserver(() => { if (root.clientWidth !== width) { width = root.clientWidth; clearTimeout(resizeTimer); resizeTimer = setTimeout(render, 80); } }).observe(root);
    } catch (error) {
      $('#sr-app').hidden = true;
      const status = $('#sr-loading'); status.hidden = false; status.className = 'loading fatal'; status.setAttribute('role', 'alert');
      status.replaceChildren(element('strong', '', 'Não foi possível carregar o dashboard.'), element('p', '', error.message),
        element('p', 'small', dataSource === 'api'
          ? 'Confira o serviço e a carga no banco. Dados antigos não serão exibidos como atuais.'
          : 'Gere o snapshot conforme o README e abra a aplicação por um servidor HTTP local.'));
    }
  }
  init();
})();
