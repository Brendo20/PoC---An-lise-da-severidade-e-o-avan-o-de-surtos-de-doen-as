from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from srag.api import create_app


class ApiTests(TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.repository.pin_snapshot.return_value = {
            "snapshot_id": "srag-fixture-2019", "loaded_at": "2026-11-12T12:45:32+00:00"}
        self.repository.dashboard.return_value = {
            "snapshot_id": "srag-fixture-2019", "database_load": {"status": "loaded"},
            "territories": {"Brasil": {"metrics": {"cases": {"value": 100}}}}}
        self.repository.metrics.return_value = {"cases": {"value": 100}}
        self.repository.series.return_value = {"daily": [], "monthly": []}
        frontend = Path(__file__).resolve().parents[1] / "frontend"
        self.client = TestClient(create_app(self.repository, frontend), raise_server_exceptions=False)
        self.addCleanup(self.client.close)

    def test_health_distinguishes_live_from_database_ready(self):
        self.assertEqual(self.client.get("/health/live").status_code, 200)
        self.repository.pin_snapshot.side_effect = ConnectionError("connection failed: private-credential")
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private-credential", response.text)
        self.assertEqual(self.client.get("/health/live").status_code, 200)

    def test_dashboard_returns_repository_contract_and_no_cache_headers(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.json(), self.repository.dashboard.return_value)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertIn("x-request-id", response.headers)
        self.repository.dashboard.assert_called_once_with()

    def test_metrics_and_series_are_pinned_to_a_snapshot(self):
        response = self.client.get("/api/metrics", params={"territory": "SP"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["loaded_at"], "2026-11-12T12:45:32+00:00")
        self.repository.metrics.assert_called_once_with("srag-fixture-2019", "SP")
        response = self.client.get("/api/series", params={"territory": "Norte"})
        self.assertEqual(response.status_code, 200)
        self.repository.series.assert_called_once_with("srag-fixture-2019", "Norte")

    def test_invalid_territory_does_not_access_database(self):
        for path in ("/api/metrics", "/api/series"):
            response = self.client.get(path, params={"territory": "SP'; DROP--"})
            self.assertEqual(response.status_code, 400)
        self.repository.pin_snapshot.assert_not_called()

    def test_storage_error_does_not_leak_connection_details(self):
        self.repository.dashboard.side_effect = RuntimeError("secret DSN password=private-key")
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private-key", response.text)
        self.assertNotIn("DSN", response.text)

    def test_frontend_uses_api_and_serves_only_public_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="srag-data-source" content="api"', response.text)
        self.assertNotIn('name="srag-data-source" content="local"', response.text)
        self.assertEqual(self.client.get("/app.js").status_code, 200)
        self.assertEqual(self.client.get("/assets/brazil-states.geojson").status_code, 200)
        for path in ("/.env", "/.git/config", "/data/snapshot.json", "/sql/001_aggregate_store.sql",
                     "/assets/../data/snapshot.json", "/src/srag/database.py"):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_no_write_endpoint(self):
        self.assertEqual(self.client.post("/api/dashboard", json={}).status_code, 405)
