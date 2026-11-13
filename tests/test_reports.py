import json
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from agent_fixtures import Client, News, Repository
from srag.agent import AnalysisValidationError, ReportAgent, historical_commentary, output_schema, validate_analysis, validation_diagnostic
from srag.api import create_app
from srag.groq_client import ProviderError
from srag.report_store import ReportError, ReportService, ReportStore
from srag.report_html import render_report


class ReportTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repository, self.client, self.news = Repository(), Client(), News()
        self.now = 1000
        self.store = ReportStore(Path(self.temp.name))
        self.service = ReportService(self.repository, self.store, self.client, self.news, lambda: self.now)

    def generate(self):
        return self.service.generate(["SP", "MG"], "fixture")

    def test_complete_report_pins_tools_numbers_and_persists_two_charts(self):
        report = self.generate()
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["metrics"]["SP"]["cases"]["value"], 100)
        self.assertEqual(len(report["series"]["SP"]["daily"]), 30)
        self.assertEqual(len(report["series"]["SP"]["monthly"]), 12)
        self.assertEqual(len(self.client.calls), 4)
        self.assertIsNone(self.client.calls[0]["schema"])
        self.assertIsNone(self.client.calls[3]["tools"])
        self.assertEqual([len(call["tools"]) for call in self.client.calls[:3]], [1, 1, 1])
        self.assertEqual([call["tools"][0]["function"]["name"] for call in self.client.calls[:3]],
                         ["consultar_metricas", "consultar_series", "buscar_noticias"])
        self.assertFalse(any(item['role'] == 'tool' for item in self.client.calls[3]['messages']))
        self.assertIn('Não solicite nem chame ferramentas', self.client.calls[3]['messages'][0]['content'])
        self.assertTrue(all(len(call['messages']) == 2 for call in self.client.calls[:3]))
        evidence = json.loads(self.client.calls[3]['messages'][1]['content'])
        self.assertNotIn('series', evidence)
        self.assertNotIn('url', evidence['news']['articles'][0])
        self.assertEqual(evidence['metrics'], report['metrics'])
        html = self.store.html(report["report_id"])
        self.assertEqual(html.count('<svg '), 2)
        self.assertIn("Não calculável", html)
        self.assertIn("não explicam causalmente", html)
        audit = (self.store.folder(report["report_id"]) / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "report_saved"', audit)
        self.assertIn('result_sha256', audit)
        self.assertNotIn('historical_commentary', audit)
        self.assertEqual(self.store.read(report["report_id"]), report)

    def test_snapshot_changed_and_invalid_scopes_never_call_model(self):
        for territories, snapshot, code in [(["SP"], "stale", "snapshot_changed_refresh_dashboard"),
                (["Brasil", "SP"], "fixture", "incompatible_comparison"),
                (["SP", "Norte"], "fixture", "incompatible_comparison"),
                (["SP", "SP"], "fixture", "invalid_territories"),
                (["DROP"], "fixture", "invalid_territories")]:
            with self.assertRaises(ReportError) as error:
                self.service.generate(territories, snapshot)
            self.assertEqual(error.exception.code, code)
        self.assertFalse(self.client.calls)

    def test_cache_cooldown_and_single_generation(self):
        first = self.generate()
        self.assertTrue(self.generate()["cached"])
        self.assertEqual(len(self.client.calls), 4)
        with self.assertRaises(ReportError) as error:
            self.service.generate(["Brasil"], "fixture")
        self.assertEqual(error.exception.status, 429)
        self.now += 301
        self.assertNotEqual(self.generate()["report_id"], first["report_id"])
        self.service.lock.acquire()
        try:
            with self.assertRaises(ReportError):
                self.generate()
        finally:
            self.service.lock.release()

    def test_unknown_tool_and_arguments_fail_closed_with_controlled_data(self):
        for function in ({"name": "executar_sql", "arguments": "{}"},
                         {"name": "buscar_noticias", "arguments": "{}"},
                         {"name": "consultar_metricas", "arguments": '{"sql":"DROP"}'}):
            class Invalid(Client):
                def complete(self, *args, **kwargs):
                    return {"message": {"tool_calls": [{"id": "x", "function": function}]},
                            "usage": {}, "response_id": "fixture"}
            events = []
            report = ReportAgent(self.repository, Invalid(), self.news).run(
                self.repository.pin_snapshot(), ["Brasil"], lambda event, **fields: events.append(event))
            self.assertEqual(report["status"], "partial")
            self.assertIsNone(report["analysis"])
            self.assertEqual(report["metrics"]["Brasil"]["cases"]["value"], 100)
            self.assertEqual(events.count("controlled_tool_fallback"), 3)

    def test_bad_draft_repair_is_bounded(self):
        class Invalid(Client):
            def complete(self, messages, **kwargs):
                result = super().complete(messages, **kwargs)
                if kwargs.get("schema"):
                    result["message"]["content"] = '{"invented":42}'
                return result
        client = Invalid()
        report = ReportAgent(self.repository, client, self.news).run(
            self.repository.pin_snapshot(), ["Brasil"], lambda *args, **kwargs: None)
        self.assertEqual(len(client.calls), 5)
        self.assertEqual(report["status"], "partial")

    def test_quota_failure_keeps_deterministic_report(self):
        class Limited(Client):
            def complete(self, *args, **kwargs):
                raise ProviderError("rate_limit", 429)
        service = ReportService(self.repository, self.store, Limited(), self.news)
        report = service.generate(["Brasil"], "fixture")
        self.assertEqual(report["status"], "partial")
        self.assertIn("rate_limit", report["warnings"])
        self.assertIn("Relatório parcial", service.store.html(report["report_id"]))

    def test_validation_rejects_numbers_citations_and_wrong_trends(self):
        report = self.generate()
        for field, value in [("historical_commentary", "Há 999 casos"),
                             ("current_commentary", "<script>alert()</script>"),
                             ("cited_news_ids", ["invented"]),
                             ("growth_trends", [{"territory": "SP", "trend": "increase"}])]:
            draft = deepcopy(report["analysis"]); draft[field] = value
            with self.assertRaises(ValueError):
                validate_analysis(draft, report["metrics"], report["news"])

    def test_http_contract_errors_storage_and_security_headers(self):
        with TestClient(create_app(self.repository, frontend=None, report_service=self.service)) as api:
            self.assertTrue(api.get('/api/agent/status').json()['configured'])
            self.assertEqual(api.post('/api/reports', json={"territories": ["SP"], "snapshot_id": "old"}).status_code, 409)
            self.assertEqual(api.post('/api/reports', json={"territories": [], "snapshot_id": "fixture"}).status_code, 422)
            self.assertEqual(api.post('/api/reports', json={"territories": ["SP"], "snapshot_id": "fixture", "sql": "DROP"}).status_code, 422)
            response = api.post('/api/reports', json={"territories": ["Brasil"], "snapshot_id": "fixture"})
            self.assertEqual(response.status_code, 200)
            identifier = response.json()['report_id']
            self.assertEqual(api.get('/api/reports/' + identifier).status_code, 200)
            html = api.get('/api/reports/' + identifier + '/html')
            self.assertIn("default-src 'none'", html.headers['content-security-policy'])
            self.assertEqual(api.get('/api/reports/invalid/html').status_code, 404)
            limited = api.post('/api/reports', json={"territories": ["SP"], "snapshot_id": "fixture"})
            self.assertEqual(limited.status_code, 429)
            self.assertEqual(limited.headers['retry-after'], '60')

    def test_no_path_traversal(self):
        with self.assertRaises(FileNotFoundError):
            self.store.read('../.env')

    def test_html_escapes_external_titles_and_refuses_unsafe_links(self):
        report = self.generate()
        report['news']['articles'][0]['title'] = '<script>external()</script>'
        html = render_report(report)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        report['news']['articles'][0]['url'] = 'javascript:alert(1)'
        self.assertNotIn('javascript:', render_report(report))

    def test_missing_news_cannot_be_marked_complete(self):
        class Empty(News):
            def search(self):
                return {**super().search(), 'status': 'unavailable', 'articles': []}
        report = ReportAgent(self.repository, self.client, Empty()).run(
            self.repository.pin_snapshot(), ['Brasil'], lambda *args, **kwargs: None)
        self.assertEqual(report['status'], 'partial')
        self.assertIn('recent_news_unavailable', report['warnings'])

    def test_text_rejections_identify_field_and_keep_existing_blocks(self):
        report = self.generate()
        for text, code in [
            ('No ano de 2019', 'narrative_numbers'),
            ('Taxa de dez %', 'narrative_numbers'),
            ('Veja https://example.org', 'narrative_markup_or_url'),
            ('<b>Exemplo</b>', 'narrative_markup_or_url'),
            ('gsk_fixture', 'narrative_credential_pattern'),
            ('sk-proj-fixture', 'narrative_credential_pattern'),
            ('Não podemos inferir eficácia.', 'narrative_efficacy_terms'),
            ('Não foi causado por isso.', 'narrative_causal_terms'),
            ('Não é devido à vacinação.', 'narrative_causal_terms')
        ]:
            draft = deepcopy(report['analysis'])
            draft['current_commentary'] = text
            with self.assertRaises(AnalysisValidationError) as error:
                validate_analysis(draft, report['metrics'], report['news'])
            self.assertEqual(validation_diagnostic(error.exception), {'reason': code, 'field': 'current_commentary'})

    def test_targeted_repair_receives_rejected_draft_without_persisting_it(self):
        class Repairable(Client):
            def complete(self, messages, **kwargs):
                result = super().complete(messages, **kwargs)
                if kwargs.get('schema') and len(self.calls) == 4:
                    draft = json.loads(result['message']['content'])
                    draft['historical_commentary'] = 'Não podemos inferir eficácia.'
                    result['message']['content'] = json.dumps(draft)
                return result
        client = Repairable()
        service = ReportService(self.repository, self.store, client, self.news)
        report = service.generate(['Brasil'], 'fixture')
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(len(client.calls), 5)
        repair = client.calls[-1]['messages']
        self.assertEqual(repair[-2]['role'], 'assistant')
        self.assertIn('narrative_efficacy_terms', repair[-1]['content'])
        self.assertIn('historical_commentary', repair[-1]['content'])
        event = next(event for event in report['audit'] if event['event'] == 'narrative_rejected')
        self.assertEqual(event['reason'], 'narrative_efficacy_terms')
        self.assertEqual(event['field'], 'historical_commentary')
        for filename in ('report.json', 'report.html', 'audit.jsonl'):
            content = (self.store.folder(report['report_id']) / filename).read_text(encoding='utf-8')
            self.assertNotIn('Não podemos inferir eficácia.', content)

    def test_validation_diagnostic_does_not_expose_unknown_exception_text(self):
        result = validation_diagnostic(ValueError('private-key detail'))
        self.assertEqual(result, {'reason': 'invalid_response', 'field': None})
        self.assertNotIn('private-key', str(result))

    def test_schema_leaves_text_rules_to_validator_and_reference_ids_separate(self):
        schema = output_schema(['Brasil'])
        for field in ('historical_commentary', 'current_commentary'):
            self.assertNotIn('pattern', schema['properties'][field])
        self.assertNotIn('pattern', schema['properties']['cited_news_ids']['items'])
        self.assertEqual(schema['properties']['growth_trends']['items']['properties']['territory']['enum'], ['Brasil'])

    def test_historical_commentary_matches_computed_trends_and_schema_enum(self):
        metrics = {'SP': self.repository.metrics('fixture', 'SP'), 'MG': self.repository.metrics('fixture', 'MG')}
        metrics['MG']['growth'] = {'status': 'available', 'value': 10}
        text = historical_commentary(metrics)
        self.assertIn('Para São Paulo, houve queda', text)
        self.assertIn('Para Minas Gerais, houve aumento', text)
        self.assertIn('não há comparação temporal desses percentuais', text)
        self.assertEqual(output_schema(['SP', 'MG'], metrics)['properties']['historical_commentary']['enum'], [text])

    def test_unsupported_historical_stability_or_vaccine_effect_is_rejected(self):
        report = self.generate()
        for claim in ('A cobertura vacinal demonstrou impacto na redução de casos graves.',
                      'A taxa de mortalidade e as internações mantiveram níveis estáveis.'):
            draft = deepcopy(report['analysis']); draft['historical_commentary'] = claim
            with self.assertRaises(ValueError) as error:
                validate_analysis(draft, report['metrics'], report['news'])
            self.assertEqual(str(error.exception), 'historical_statement_mismatch')

    def test_legacy_publication_withdraws_invalid_text_without_modifying_evidence(self):
        report = self.generate()
        identifier, _, _ = self.store.start()
        legacy = deepcopy(report); legacy['report_id'] = identifier
        legacy['analysis']['historical_commentary'] = 'A cobertura vacinal demonstrou impacto na redução de casos graves.'
        legacy['prompt_version'] = 'srag-2019-v5-targeted-repair'
        self.store.save(legacy, render_report(legacy))
        path = self.store.folder(identifier) / 'report.json'
        original = path.read_bytes()
        reviewed = self.store.read(identifier)
        self.assertEqual(reviewed['status'], 'partial')
        self.assertIsNone(reviewed['analysis'])
        self.assertEqual(reviewed['publication_review']['reason'], 'historical_statement_mismatch')
        self.assertNotIn('demonstrou impacto', self.store.html(identifier))
        self.assertIn('Narrativa anterior retirada', self.store.html(identifier))
        self.assertEqual(path.read_bytes(), original)
