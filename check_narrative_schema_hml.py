"""Sondagem real do schema com evidências salvas; não muda relatórios nem requer rebuild.

Uso: docker compose -f compose.hml.yml exec -T api python - REPORT_ID < check_narrative_schema_hml.py
Realiza somente uma chamada LLM. O módulo srag já deve estar instalado no container.
"""
import json
import re
import sys
import urllib.request

from srag.agent import NARRATIVE_SYSTEM, output_schema, validate_analysis
from srag.groq_client import GroqClient, ProviderError


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[a-f0-9]{32}', sys.argv[1]):
        raise SystemExit('Informe um report_id válido.')
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/api/reports/' + sys.argv[1], timeout=15) as response:
            report = json.load(response)
    except (OSError, ValueError):
        raise SystemExit('Não foi possível ler o relatório salvo na API local.') from None

    schema = output_schema(report['territories'])
    # Aplicado aqui também para sondar o contrato antes de reconstruir uma imagem antiga.
    for field in ('historical_commentary', 'current_commentary'):
        schema['properties'][field].update(pattern=r'^[^0-9%<>]*$',
            description='Texto qualitativo sem algarismos, datas, percentuais, HTML ou IDs; referências somente em cited_news_ids.')
    evidence = {'territories': report['territories'], 'reference': report['reference'],
        'metrics': report['metrics'], 'news': {'status': report['news']['status'], 'articles': [
            {key: article[key] for key in ('id', 'title', 'excerpt', 'source', 'published_at')}
            for article in report['news']['articles']]}}
    try:
        response = GroqClient().complete([
            {'role': 'system', 'content': NARRATIVE_SYSTEM},
            {'role': 'user', 'content': json.dumps(evidence, ensure_ascii=False)}], schema=schema)
        draft = json.loads(response['message']['content'])
        validate_analysis(draft, report['metrics'], report['news'])
    except ProviderError as error:
        print(json.dumps({'status': 'failed', 'error': error.code, **error.diagnostic()}, ensure_ascii=False))
        return 1
    except (ValueError, TypeError, KeyError) as error:
        from srag.agent import validation_diagnostic
        print(json.dumps({'status': 'rejected', **validation_diagnostic(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({'status': 'passed', 'narrativa_validada': True,
        'relatorio_de_origem': report['report_id'], 'relatorio_original_alterado': False,
        'chamadas_llm': 1, 'tokens': response['usage']}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
