from contextlib import nullcontext
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import MagicMock

from srag.database import PostgresRepository, TERRITORIES, content_hash, load_snapshot, validate_snapshot


def snapshot():
    document = {"metrics": {"icu_occupancy": {"value": None},
                             "population_vaccination": {"value": None}},
                "daily": [{}] * 30, "monthly": [{}] * 12}
    return {"schema_version": "1.0.0", "snapshot_id": "test-snapshot", "source": {"sha256": "a" * 64},
            "reference": "2019-12-28", "generated_at": "2026-11-11T12:00:00Z",
            "database_load": {"loaded_at": None},
            "privacy": {"audience": "local_development_only"},
            "territories": {key: document for key in TERRITORIES}}


class DatabaseTests(TestCase):
    def test_fingerprint_ignores_execution_time_not_analytical_content(self):
        first, second = snapshot(), snapshot()
        second["generated_at"] = "2026-11-12T12:00:00Z"
        self.assertEqual(content_hash(first), content_hash(second))
        second["reference"] = "2019-12-27"
        self.assertNotEqual(content_hash(first), content_hash(second))

    def test_invalid_geography_or_fake_metric_rejected(self):
        data = snapshot()
        data["territories"].pop("AC")
        with self.assertRaisesRegex(ValueError, "27 UFs"):
            validate_snapshot(data)
        data = snapshot()
        data["territories"]["Brasil"]["metrics"]["icu_occupancy"]["value"] = 70
        with self.assertRaisesRegex(ValueError, "denominador"):
            validate_snapshot(data)

    def test_untrusted_territory_never_opens_database(self):
        factory = MagicMock()
        repository = PostgresRepository(factory)
        with self.assertRaisesRegex(ValueError, "Território"):
            repository.territory("snapshot", "SP'; DROP SCHEMA srag; --")
        factory.assert_not_called()

    def test_query_uses_read_only_and_bound_parameters(self):
        connection = MagicMock()
        connection.execute.return_value.fetchone.return_value = ({"metrics": {}},)
        repository = PostgresRepository(lambda: nullcontext(connection))
        malicious_id = "snapshot' OR true --"
        repository.territory(malicious_id, "SP")
        calls = connection.execute.call_args_list
        self.assertEqual(calls[0].args, ("SET TRANSACTION READ ONLY",))
        sql, parameters = calls[-1].args
        self.assertNotIn(malicious_id, sql)
        self.assertEqual(parameters, (malicious_id, "SP"))

    def test_missing_active_load_is_explicit(self):
        connection = MagicMock()
        connection.execute.return_value.fetchone.return_value = None
        repository = PostgresRepository(lambda: nullcontext(connection))
        with self.assertRaisesRegex(LookupError, "Nenhuma carga ativa"):
            repository.pin_snapshot()

    def test_conflicting_load_does_not_promote_snapshot(self):
        connection = MagicMock()
        connection.transaction.return_value = nullcontext()
        connection.execute.return_value.fetchone.return_value = ("different-hash", datetime.now(timezone.utc))
        with self.assertRaisesRegex(ValueError, "conteúdo diferente"):
            load_snapshot(connection, snapshot())
        self.assertFalse(any("INSERT" in call.args[0] for call in connection.execute.call_args_list))

    def test_idempotent_load_preserves_loaded_at(self):
        connection = MagicMock()
        connection.transaction.return_value = nullcontext()
        data = snapshot()
        original_time = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)
        connection.execute.return_value.fetchone.return_value = (content_hash(data), original_time)
        result = load_snapshot(connection, data)
        self.assertEqual(result["status"], "already_loaded")
        self.assertEqual(result["loaded_at"], original_time.isoformat())
        calls = [call.args[0] for call in connection.execute.call_args_list]
        self.assertFalse(any("INSERT INTO srag.territory_aggregates" in sql for sql in calls))
        self.assertTrue(any("INSERT INTO srag.active_snapshot" in sql for sql in calls))
