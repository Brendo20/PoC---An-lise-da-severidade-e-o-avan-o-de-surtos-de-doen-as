import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from srag.profile import CODE_FIELDS, DATE_FIELDS, normalize_code, parse_date, profile_csv


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sample.csv"

    def write_rows(self, rows):
        fields = ["NU_NOTIFIC", *DATE_FIELDS, *CODE_FIELDS]
        with self.path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)

    def run_profile(self):
        return profile_csv(self.path, as_of=date(2026, 11, 10), source_url="https://example.org/data")

    def test_dates_and_codes(self):
        self.assertEqual(normalize_code(" 2.0 "), "2")
        self.assertEqual(normalize_code("2.5"), "2.5")
        self.assertEqual(parse_date("28/12/2019"), date(2019, 12, 28))
        self.assertEqual(parse_date("2019-07-22T00:00:00.000Z"), date(2019, 7, 22))
        with self.assertRaises(ValueError):
            parse_date("2019-02-30")

    def test_quality_privacy_and_reproducibility(self):
        self.write_rows([
            {"NU_NOTIFIC": "PRIVATE-ID-001", "DT_SIN_PRI": "2019-12-28",
             "DT_NOTIFIC": "2019-12-27", "DT_INTERNA": "2109-07-10", "UTI": "1",
             "DT_ENTUTI": "2019-12-29", "DT_SAIDUTI": "2019-12-28", "EVOLUCAO": "2.0"},
            {"NU_NOTIFIC": "PRIVATE-ID-001", "DT_SIN_PRI": "2019-12-27", "UTI": "9",
             "VACINA": "untrusted raw content", "DT_INTERNA": "bad date"},
        ])
        result = self.run_profile()
        again = self.run_profile()
        self.assertEqual(result["source"]["sha256"], again["source"]["sha256"])
        self.assertEqual(result["analysis_id"], again["analysis_id"])
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["issues"]["repeated_notification_id"], 1)
        self.assertEqual(result["issues"]["notification_before_symptoms"], 1)
        self.assertEqual(result["issues"]["icu_exit_before_entry"], 1)
        self.assertEqual(result["dates"]["DT_INTERNA"]["future"], 1)
        self.assertEqual(result["dates"]["DT_INTERNA"]["invalid"], 1)
        self.assertEqual(result["codes"]["EVOLUCAO"]["2"], 1)
        self.assertEqual(result["codes"]["UTI"]["9"], 1)
        self.assertEqual(result["analytical_reference_candidate"], "2019-12-28")
        self.assertNotIn("PRIVATE-ID", json.dumps(result))
        self.assertNotIn("untrusted raw content", json.dumps(result))
        self.assertIsNone(result["database_load"]["loaded_at"])

    def test_future_symptoms_do_not_extend_reference(self):
        self.write_rows([{"DT_SIN_PRI": "2019-12-28"}, {"DT_SIN_PRI": "2109-01-01"}])
        result = self.run_profile()
        self.assertEqual(result["analytical_reference_candidate"], "2019-12-28")
        self.assertEqual(result["dates"]["DT_SIN_PRI"]["future"], 1)

    def test_missing_schema_is_rejected(self):
        self.path.write_text("unrelated;column\n1;2\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Colunas obrigatórias"):
            self.run_profile()

    def test_empty_file_is_rejected(self):
        self.write_rows([])
        with self.assertRaisesRegex(ValueError, "sem registros"):
            self.run_profile()

    def test_malformed_rows_are_quarantined(self):
        self.write_rows([{"DT_SIN_PRI": "2019-12-28"}])
        with self.path.open("a", encoding="utf-8") as f:
            f.write("short;row\n")
        result = self.run_profile()
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["malformed_rows"], 1)


if __name__ == "__main__":
    unittest.main()
