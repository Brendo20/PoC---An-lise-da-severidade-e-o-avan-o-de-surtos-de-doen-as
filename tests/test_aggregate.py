import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from srag.aggregate import build_snapshot, growth, percentage


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "sample.csv"

    def write(self, rows):
        with self.source.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["DT_SIN_PRI", "SG_UF", "EVOLUCAO", "UTI", "VACINA"], delimiter=";")
            writer.writeheader()
            writer.writerows(rows)

    def build(self, start=date(2018, 12, 30)):
        return build_snapshot(self.source, reference=date(2019, 12, 28),
                              coverage_start=start, coverage_end=date(2019, 12, 28))

    def test_realistic_windows_geography_and_unknowns(self):
        rows = []
        for day, count in [("2019-12-28", 10), ("2019-12-21", 5), ("2019-01-01", 5)]:
            rows += [{"DT_SIN_PRI": day, "SG_UF": "SP", "EVOLUCAO": "2.0", "UTI": "2", "VACINA": "1"}] * count
        rows += [{"DT_SIN_PRI": "2018-12-30", "SG_UF": "SP"}] * 5
        rows += [{"DT_SIN_PRI": "2019-12-27", "SG_UF": "ZZ", "EVOLUCAO": "1"}] * 5
        self.write(rows)
        result = self.build()
        brasil = result["territories"]["Brasil"]
        sp = result["territories"]["SP"]
        self.assertEqual(result["audit"]["input_rows"], 30)
        self.assertEqual(result["audit"]["issues"]["unknown_residence_uf"], 5)
        self.assertEqual(brasil["metrics"]["cases"]["value"], 25)
        self.assertEqual(sp["metrics"]["cases"]["value"], 20)
        self.assertEqual(sp["metrics"]["growth"]["value"], 100)
        self.assertEqual(brasil["metrics"]["fatality"]["value"], 80)
        self.assertEqual(sp["metrics"]["cases"], result["territories"]["Sudeste"]["metrics"]["cases"])
        self.assertEqual(len(sp["daily"]), 30)
        self.assertEqual(sp["daily"][0]["date"], "2019-11-29")
        self.assertEqual(len(sp["monthly"]), 12)
        self.assertTrue(sp["monthly"][-1]["partial"])
        self.assertIsNone(result["database_load"]["loaded_at"])

    def test_small_counts_not_exported_and_zero_distinct(self):
        self.write([{"DT_SIN_PRI": "2019-12-28", "SG_UF": "AC", "EVOLUCAO": "2"}])
        result = self.build()
        ac = result["territories"]["AC"]
        self.assertEqual(ac["metrics"]["cases"], {"value": None, "status": "suppressed"})
        self.assertEqual(ac["daily"][-1]["status"], "suppressed")
        self.assertNotIn("numerator", ac["metrics"]["fatality"])
        self.assertEqual(result["territories"]["SP"]["daily"][-1]["value"], 0)
        self.assertNotIn("DT_SIN_PRI", json.dumps(result))

    def test_uncovered_period_is_not_zero(self):
        self.write([{"DT_SIN_PRI": "2019-12-28", "SG_UF": "SP"}] * 5)
        result = self.build(start=date(2019, 12, 1))
        sp = result["territories"]["SP"]
        self.assertEqual(sp["daily"][0]["status"], "unavailable")
        self.assertEqual(sp["monthly"][0]["status"], "unavailable")
        self.assertEqual(sp["metrics"]["cases"]["status"], "unavailable")

    def test_rates_zero_missing_and_suppression(self):
        self.assertEqual(growth(10, 5)["value"], 100)
        self.assertEqual(growth(0, 5)["value"], -100)
        self.assertEqual(growth(5, 0)["reason"], "zero_denominator")
        self.assertEqual(percentage(5, 10, 10)["unknown_percent"], 50)
        self.assertEqual(percentage(0, 0)["reason"], "zero_denominator")
        self.assertEqual(percentage(2, 100)["status"], "suppressed")
        self.assertEqual(percentage(100, 102)["status"], "suppressed")
        self.assertEqual(percentage(10, 100, 2)["status"], "suppressed")

    def test_invalid_and_outside_dates_are_audited(self):
        self.write([{"DT_SIN_PRI": "bad"}, {"DT_SIN_PRI": "2017-01-01"},
                    {"DT_SIN_PRI": "2019-12-28", "SG_UF": "SP"}])
        result = self.build()
        self.assertEqual(result["audit"]["issues"]["invalid_symptom_date"], 1)
        self.assertEqual(result["audit"]["issues"]["outside_declared_coverage"], 1)

    def test_reference_outside_coverage_rejected(self):
        self.write([])
        with self.assertRaisesRegex(ValueError, "Referência"):
            self.build(start=date(2020, 1, 1))
