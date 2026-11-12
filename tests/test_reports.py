import json
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from agent_fixtures import Client, News, Repository
from srag.agent import ReportAgent, validate_analysis
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
