"""Sondagem real do schema com evidências salvas; não muda relatórios nem requer rebuild.

Uso: docker compose -f compose.hml.yml exec -T api python - REPORT_ID < check_narrative_schema_hml.py
Realiza somente uma chamada LLM. O módulo srag já deve estar instalado no container.
"""
import json
import argparse
import re
import urllib.request

from srag.agent import NARRATIVE_SYSTEM, output_schema, validate_analysis
from srag.groq_client import GroqClient, ProviderError


def numeric_fragments(draft, secret):
    """Trechos limitados de comentários, sem mensagem de raciocínio ou credenciais."""
    fragments = []
    if not isinstance(draft, dict):
        return fragments
    for field in ('historical_commentary', 'current_commentary'):
        text = draft.get(field)
        if not isinstance(text, str):
            continue
        if secret:
            text = text.replace(secret, '[CHAVE OCULTA]')
        text = re.sub(r'(?:gsk_|sk-proj-)[A-Za-z0-9_-]+', '[CHAVE OCULTA]', text)
        for match in list(re.finditer(r'\d+|%', text))[:5]:
            fragment = text[max(0, match.start() - 20):min(len(text), match.end() + 28)]
            fragments.append({'field': field, 'fragment': fragment})
    return fragments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report_id')
    parser.add_argument('--inspect-numbers', action='store_true',
                        help='Usar schema sem pattern e mostrar apenas trechos numéricos limitados.')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{32}', args.report_id):
        raise SystemExit('Informe um report_id válido.')
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/api/reports/' + args.report_id, timeout=15) as response:
            report = json.load(response)
    except (OSError, ValueError):
        raise SystemExit('Não foi possível ler o relatório salvo na API local.') from None

    schema = output_schema(report['territories'])
    for field in ('historical_commentary', 'current_commentary'):
        if args.inspect_numbers:
            schema['properties'][field].pop('pattern', None)
        else:
            # Experimento apenas na sondagem; não faz parte do schema implantável.
            schema['properties'][field].update(pattern=r'^[^0-9%<>]*$',
                description='Texto qualitativo sem algarismos, datas, percentuais, HTML ou IDs; referências somente em cited_news_ids.')
    evidence = {'territories': report['territories'], 'reference': report['reference'],
        'metrics': report['metrics'], 'news': {'status': report['news']['status'], 'articles': [
            {key: article[key] for key in ('id', 'title', 'excerpt', 'source', 'published_at')}
            for article in report['news']['articles']]}}
    client = GroqClient()
    draft = None
    try:
        response = client.complete([
            {'role': 'system', 'content': NARRATIVE_SYSTEM},
            {'role': 'user', 'content': json.dumps(evidence, ensure_ascii=False)}], schema=schema)
        draft = json.loads(response['message']['content'])
        validate_analysis(draft, report['metrics'], report['news'])
    except ProviderError as error:
        print(json.dumps({'status': 'failed', 'error': error.code, **error.diagnostic()}, ensure_ascii=False))
        return 1
    except (ValueError, TypeError, KeyError) as error:
        from srag.agent import validation_diagnostic
        diagnostic = {'status': 'rejected', **validation_diagnostic(error)}
        if args.inspect_numbers:
            diagnostic['numeric_fragments'] = numeric_fragments(draft, client.key)
        print(json.dumps(diagnostic, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({'status': 'passed', 'narrativa_validada': True,
        'relatorio_de_origem': report['report_id'], 'relatorio_original_alterado': False,
        'chamadas_llm': 1, 'tokens': response['usage']}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
