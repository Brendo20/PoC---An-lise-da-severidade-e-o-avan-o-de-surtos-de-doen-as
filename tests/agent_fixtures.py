"""Dublês explícitos: não realizam conexão com PostgreSQL, notícias ou Groq."""
import json
from datetime import date, timedelta

from srag.agent import trend


class Repository:
    def pin_snapshot(self):
        return {"snapshot_id": "fixture", "loaded_at": "2026-11-12T12:45:32+00:00", "metadata": {
            "reference": "2019-12-28", "window_start": "2019-01-01",
            "source": {"filename": "synthetic.csv", "sha256": "a" * 64}}}

    def metrics(self, identifier, territory):
        assert identifier == "fixture"
        values = {key: {"status": "available", "value": value} for key, value in {
            "cases": 100, "growth": -10, "fatality": 10,
            "icu_admission": 30, "flu_vaccination_cases": 20}.items()}
        for key in ("icu_occupancy", "population_vaccination"):
            values[key] = {"status": "unavailable", "value": None}
        return values

    def series(self, identifier, territory):
        assert identifier == "fixture"
        return {"daily": [{"date": (date(2019, 11, 29) + timedelta(days=i)).isoformat(),
                            "value": 10, "status": "available"} for i in range(30)],
                "monthly": [{"date": f"2019-{i:02}-01", "value": 100,
                             "status": "available", "partial": i == 12} for i in range(1, 13)]}


class News:
    def search(self):
        return {"status": "available", "retrieved_at": "2026-11-12T12:00:00+00:00",
                "method": "Fixture: títulos e resumos", "scope": "Brasil", "window_days": 30,
                "errors": [], "articles": [{"id": "news-fixture", "title": "Fixture de notícia SRAG",
                    "excerpt": "Exemplo sintético", "url": "https://example.org/srag",
                    "source": "Fixture", "discovery": "Fixture",
                    "published_at": "2026-11-11T12:00:00+00:00"}]}


class Client:
    configured = True
    model = "openai/gpt-oss-20b"

    def __init__(self):
        self.calls = []

    def complete(self, messages, *, tools=None, schema=None):
        self.calls.append({"tools": tools, "schema": schema, "messages": messages.copy()})
        if tools:
            message = {"tool_calls": [{"id": f"call-{i}", "type": "function", "function": {
                "name": tool["function"]["name"], "arguments": "{}"}} for i, tool in enumerate(tools[:1])]}
        else:
            # Derivar tendências exclusivamente do resultado controlado da ferramenta.
            metrics = json.loads(messages[1]["content"])["metrics"]
            message = {"content": json.dumps({"historical_commentary": "O recorte apresenta variação dos registros e exige atenção aos dados ausentes.",
                "current_commentary": "Os títulos recentes abordam SRAG; a leitura integral das matérias não foi realizada.",
                "cited_news_ids": ["news-fixture"],
                "growth_trends": [{"territory": t, "trend": trend(m["growth"])} for t, m in metrics.items()]})}
        return {"message": message, "usage": {"total_tokens": 10}, "response_id": "fixture-response"}
