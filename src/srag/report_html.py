"""Relatório independente e imprimível; números e gráficos não são escritos pelo LLM."""
from __future__ import annotations

import html
import math
from datetime import datetime

from srag.aggregate import STATES
from srag.news import safe_url

NAMES = {uf: name for _, uf, name, _ in STATES}


def escape(value) -> str:
    return html.escape(str(value), quote=True)


def number(value: float, digits=0) -> str:
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def display(metric: dict, percent=False) -> str:
    if metric["status"] != "available":
        return "Suprimido" if metric["status"] == "suppressed" else "Não calculável"
    return number(metric["value"], 2 if percent else 0) + ("%" if percent else "")


def chart(report: dict, kind: str) -> str:
    width, height, left, right, top, bottom = 720, 230, 55, 15, 15, 35
    series = [(territory, report["series"][territory][kind]) for territory in report["territories"]]
    values = [point["value"] for _, points in series for point in points if point["status"] == "available"]
    maximum = max(1, max(values, default=0))
    maximum = math.ceil(maximum / 10) * 10
    count = len(series[0][1])
    x = lambda index: left + index / max(1, count - 1) * (width - left - right)
    y = lambda value: height - bottom - value / maximum * (height - top - bottom)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Casos por período; valores na tabela seguinte">']
    for tick in (0, maximum / 2, maximum):
        parts.append(f'<line x1="{left}" x2="{width-right}" y1="{y(tick):.2f}" y2="{y(tick):.2f}" stroke="#dce3ed"/>')
        parts.append(f'<text x="{left-8}" y="{y(tick)+4:.2f}" text-anchor="end">{number(tick)}</text>')
    for index, (territory, points) in enumerate(series):
        color = "#245fbb" if index == 0 else "#956124"
        segments, started = [], False
        for i, point in enumerate(points):
            if point["status"] != "available":
                started = False
                continue
            px, py = x(i), y(point["value"])
            segments.append(f'{"L" if started else "M"}{px:.2f},{py:.2f}')
            started = True
            title = escape(f'{NAMES.get(territory, territory)} · {point["date"]}: {point["value"]} casos')
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.5" fill="{color}"><title>{title}</title></circle>')
        dash = 'stroke-dasharray="6 4"' if index else ''
        parts.append(f'<path d="{" ".join(segments)}" fill="none" stroke="{color}" stroke-width="2" {dash}/>')
    points = series[0][1]
    for index, anchor in ((0, "start"), (count - 1, "end")):
        label = datetime.fromisoformat(points[index]["date"]).strftime("%d/%m/%Y")
        parts.append(f'<text x="{x(index):.2f}" y="{height-8}" text-anchor="{anchor}">{escape(label)}</text>')
    parts.append('</svg><p class="small">' + ' · '.join(escape(NAMES.get(t, t)) + (' (tracejado)' if i else ' (contínuo)')
                  for i, (t, _) in enumerate(series)) + '</p>')
    parts.append('<details><summary>Valores e períodos</summary><table><thead><tr><th>Período</th>')
    parts.extend(f'<th>{escape(NAMES.get(t, t))}</th>' for t, _ in series)
    parts.append('</tr></thead><tbody>')
    for i, point in enumerate(points):
        parts.append('<tr><th>' + escape(point['date']) + (' (parcial)' if point.get('partial') else '') + '</th>')
        for _, values in series:
            p = values[i]
            value = display(p) if p['status'] != 'suppressed' else '< 5 · suprimido'
            parts.append('<td>' + escape(value) + '</td>')
        parts.append('</tr>')
    parts.append('</tbody></table></details>')
    return ''.join(parts)


def render_report(report: dict) -> str:
    title = 'Relatório SRAG — ' + ' × '.join(NAMES.get(t, t) for t in report['territories'])
    parts = ['<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<meta name="robots" content="noindex,nofollow">',
             '<title>' + escape(title) + '</title>',
             '<style>body{font:15px/1.6 system-ui;color:#17273b;background:#f6f8fb;margin:0}main{max-width:1000px;margin:auto;padding:28px}h1{font-size:26px}h2{font-size:20px;margin-top:30px}h3{font-size:16px}section{background:#fff;border:1px solid #dce3ed;padding:20px;border-radius:10px;margin:16px 0}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #dce3ed;text-align:left;padding:8px;overflow-wrap:anywhere}svg{width:100%;height:auto}svg text{font:12px system-ui;fill:#526277}.small{font-size:12px;color:#526277;overflow-wrap:anywhere}a{color:#245fbb}summary{cursor:pointer}@media(max-width:600px){main{padding:12px}section{padding:12px}table{font-size:12px}}@media print{body{background:#fff}main{max-width:none}section{break-inside:avoid}details{display:block}}</style></head><body><main>',
             '<h1>' + escape(title) + '</h1>',
             '<p>Referência histórica: ' + escape(report['reference']) + ' · início do recorte: ' + escape(report['window_start']) + '</p>',
             '<p class="small">Gerado em ' + escape(report['generated_at']) + ' · carga: ' + escape(report['loaded_at']) + '</p>',
             '<p><strong>' + ('Relatório completo' if report['status'] == 'complete' else 'Relatório parcial — consulte as limitações') + '</strong></p>',
             '<section><h2>Indicadores do recorte</h2><table><thead><tr><th>Indicador</th>']
    parts.extend('<th>' + escape(NAMES.get(t, t)) + '</th>' for t in report['territories'])
    parts.append('</tr></thead><tbody>')
    for key, label in [('cases', 'Casos registrados'), ('growth', 'Crescimento em sete dias'),
                       ('fatality', 'Letalidade entre desfechos conhecidos'),
                       ('icu_admission', 'Internação em UTI entre casos com informação'),
                       ('flu_vaccination_cases', 'Vacinação contra gripe entre casos com informação'),
                       ('icu_occupancy', 'Ocupação operacional de UTI'),
                       ('population_vaccination', 'Cobertura vacinal populacional')]:
        parts.append('<tr><th>' + escape(label) + '</th>')
        for territory in report['territories']:
            item = report['metrics'][territory][key]
            note = ''
            if item['status'] == 'available' and 'denominator' in item:
                note = f'<br><span class="small">{number(item["numerator"])}/{number(item["denominator"])}'
                if 'unknown_percent' in item:
                    note += ' · sem informação: ' + number(item['unknown_percent'], 2) + '%'
                note += '</span>'
            elif key == 'growth' and item.get('reason') == 'zero_denominator':
                note = '<br><span class="small">Sem casos no período anterior</span>'
            parts.append('<td>' + escape(display(item, key != 'cases')) + note + '</td>')
        parts.append('</tr>')
    parts.append('</tbody></table><p class="small">Crescimento: (últimos sete dias / sete anteriores − um) × cem. Letalidade: óbitos por SRAG / desfechos conhecidos. UTI e vacinação: respostas sim / respostas sim ou não; ignorados e vazios são desconhecidos. Mortalidade populacional não calculável nesta base.</p></section>')
    parts.append('<section><h2>Análise histórica do recorte</h2>')
    analysis = report.get('analysis')
    parts.append('<p>' + escape(analysis['historical_commentary'] if analysis else 'Comentário do LLM indisponível ou rejeitado pela validação. Os dados e gráficos abaixo são determinísticos.') + '</p></section>')
    for kind, label in [('daily', 'Casos diários — últimos trinta dias da referência'), ('monthly', 'Casos mensais — últimos doze meses da referência')]:
        parts.append('<section><h2>' + label + '</h2>' + chart(report, kind) + '<p class="small">Lacunas não são zeros. Contagens pequenas são suprimidas. O último mês pode estar parcial.</p></section>')
    news = report['news']
    parts.append('<section><h2>Notícias atuais — contexto separado</h2><p>Notícias atuais não explicam causalmente os casos históricos de 2019.</p>')
    if analysis and analysis['current_commentary']:
        parts.append('<p>' + escape(analysis['current_commentary']) + '</p>')
        parts.append('<p class="small">Referências do comentário: ' + escape(', '.join(analysis['cited_news_ids'])) + '</p>')
    if not news['articles']:
        parts.append('<p>Nenhuma notícia recente verificada disponível nesta consulta.</p>')
    for article in news['articles']:
        if not safe_url(article['url']):
            continue
        parts.append('<h3><a target="_blank" rel="noopener noreferrer" href="' + escape(article['url']) + '">' + escape(article['title']) + '</a></h3>')
        parts.append('<p class="small">' + escape(article['id']) + ' · ' + escape(article['source']) + ' · publicado em ' + escape(article['published_at']) + ' · descoberta: ' + escape(article['discovery']) + '</p>')
    parts.append('<p class="small">Consulta em ' + escape(news['retrieved_at']) + '. ' + escape(news['method']) + '. ' + escape(news['scope']) + '.</p></section>')
    parts.append('<section><h2>Limitações e rastreabilidade</h2><ul>')
    parts.extend('<li>' + escape(item) + '</li>' for item in report['limitations'])
    parts.append('</ul><p class="small">Avisos: ' + escape(', '.join(report['warnings']) or 'nenhum') + '</p>')
    parts.append('<p class="small">Execução: ' + escape(report['report_id']) + ' · snapshot: ' + escape(report['snapshot_id']) + ' · modelo: ' + escape(report['model']) + ' · prompt: ' + escape(report['prompt_version']) + '</p>')
    parts.append('<p class="small">Origem: ' + escape(report['source']['filename']) + ' · SHA-256: ' + escape(report['source']['sha256']) + '</p>')
    parts.append('<details><summary>Eventos de auditoria</summary><ul>')
    parts.extend('<li class="small">' + escape(event['at'] + ' · ' + event['event']) + '</li>' for event in report['audit'])
    parts.append('</ul></details></section></main></body></html>')
    return ''.join(parts)
