"""Teste operacional: uma geração real; executar por stdin no container da API."""
import json
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:8000'


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as response:
        return json.load(response)


status = get('/api/agent/status')
if not status['configured']:
    raise SystemExit('Agente não configurado. Confira GROQ_API_KEY e GROQ_MODEL no .env, sem exibir a chave.')
dashboard = get('/api/dashboard')
request = urllib.request.Request(BASE + '/api/reports',
    data=json.dumps({'territories': ['Brasil'], 'snapshot_id': dashboard['snapshot_id']}).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(request, timeout=180) as response:
        report = json.load(response)
except urllib.error.HTTPError as error:
    try:
        code = json.load(error).get('detail', 'request_failed')
    except (ValueError, AttributeError):
        code = 'request_failed'
    raise SystemExit(f'Falha na geração: HTTP {error.code}, {code}') from None
except urllib.error.URLError:
    raise SystemExit('Falha de conexão com o serviço local da API.') from None

assert report['snapshot_id'] == dashboard['snapshot_id'], 'Snapshot divergente'
assert report['metrics']['Brasil'] == dashboard['territories']['Brasil']['metrics'], 'Métricas divergentes'
assert len(report['series']['Brasil']['daily']) == 30
assert len(report['series']['Brasil']['monthly']) == 12
with urllib.request.urlopen(BASE + '/api/reports/' + report['report_id'] + '/html', timeout=15) as response:
    assert response.read().count(b'<svg ') == 2, 'Relatório sem os dois gráficos'
print(json.dumps({
    'status': report['status'], 'report_id': report['report_id'], 'modelo': report['model'],
    'prompt_version': report['prompt_version'],
    'snapshot_id': report['snapshot_id'], 'carga': report['loaded_at'],
    'noticias': len(report['news']['articles']), 'narrativa_validada': report['analysis'] is not None,
    'avisos': report['warnings'], 'cache': report['cached'], 'eventos_auditoria': len(report['audit']),
    'rodadas_ferramentas': sum(event['event'] == 'llm_tool_round' for event in report['audit']),
    'rejeicoes_narrativa': [{key: event.get(key) for key in ('attempt', 'reason', 'field')}
                           for event in report['audit'] if event['event'] == 'narrative_rejected'],
    'erros_provedor': [{key: event.get(key) for key in ('event', 'error_code', 'http_status', 'provider_code', 'retry_after_seconds')}
                       for event in report['audit'] if event.get('http_status') is not None],
    'relatorio': '/api/reports/' + report['report_id'] + '/html'
}, ensure_ascii=False, indent=2))
if report['status'] != 'complete':
    raise SystemExit('Relatório parcial preservado. Revisar os avisos antes de aceitar a integração LLM.')
