"""Auditoria dos campos UTI/vacinação, sem exportar registros individuais."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

from srag.profile import normalize_code, parse_date


def investigate(source: Path) -> dict:
    scopes = {name: Counter() for name in ("full_file", "calendar_2019")}
    icu = Counter()
    vaccine = Counter()
    hospital_pairs = Counter()
    with source.open("rb") as stream:
        fingerprint = hashlib.file_digest(stream, "sha256").hexdigest()
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";", strict=True)
        columns = reader.fieldnames or []
        for row in reader:
            symptom_date = parse_date(row["DT_SIN_PRI"])
            admission = normalize_code(row["HOSPITAL"])
            uti = normalize_code(row["UTI"])
            vac = normalize_code(row["VACINA"])
            targets = ["full_file"]
            if symptom_date and date(2019, 1, 1) <= symptom_date <= date(2019, 12, 28):
                targets.append("calendar_2019")
            for name in targets:
                counts = scopes[name]
                counts["rows"] += 1
                counts["icu_" + (uti or "missing")] += 1
                counts["vaccine_" + (vac or "missing")] += 1
                if admission == "1":
                    counts["hospitalized"] += 1
                    counts["hospital_icu_" + (uti or "missing")] += 1
            hospital_pairs[f"icu={uti or 'missing'};hospital={admission or 'missing'}"] += 1
            if uti == "1":
                start = parse_date(row["DT_ENTUTI"])
                end = parse_date(row["DT_SAIDUTI"])
                icu["reported_yes"] += 1
                if start is None:
                    icu["missing_entry"] += 1
                if end is None:
                    icu["missing_exit"] += 1
                if start and end:
                    icu["both_dates"] += 1
                    if end < start:
                        icu["exit_before_entry"] += 1
                    elif symptom_date and start < symptom_date:
                        icu["entry_before_symptoms_among_complete_intervals"] += 1
                    else:
                        icu["coherent_complete_interval"] += 1
                        if start == end:
                            icu["same_day_entry_exit"] += 1
                        if (end - start).days > 365:
                            icu["stay_over_365_days"] += 1
            if vac == "1":
                dose = parse_date(row["DT_UT_DOSE"])
                vaccine["reported_yes"] += 1
                if dose:
                    vaccine["yes_with_date"] += 1
                    if symptom_date and dose > symptom_date:
                        vaccine["dose_after_symptoms"] += 1
                    if dose.year != 2019:
                        vaccine["dose_outside_2019"] += 1
                else:
                    vaccine["yes_without_date"] += 1
            elif row["DT_UT_DOSE"]:
                vaccine["date_without_yes"] += 1
            if any(row[key] for key in ("DT_DOSEUNI", "DT_1_DOSE", "DT_2_DOSE")):
                vaccine["any_child_dose_date"] += 1
    rates = {}
    for name, counts in scopes.items():
        icu_known = counts["icu_1"] + counts["icu_2"]
        vaccinated_known = counts["vaccine_1"] + counts["vaccine_2"]
        hospital_known = counts["hospital_icu_1"] + counts["hospital_icu_2"]
        rates[name] = {
            "icu_known_denominator": icu_known,
            "icu_among_known_percent": 100 * counts["icu_1"] / icu_known if icu_known else None,
            "icu_unknown_percent": 100 * (counts["icu_missing"] + counts["icu_9"]) / counts["rows"],
            "hospital_icu_known_denominator": hospital_known,
            "icu_among_hospitalized_known_percent": 100 * counts["hospital_icu_1"] / hospital_known if hospital_known else None,
            "vaccination_known_denominator": vaccinated_known,
            "vaccination_among_known_cases_percent": 100 * counts["vaccine_1"] / vaccinated_known if vaccinated_known else None,
            "vaccination_confirmed_among_all_cases_percent": 100 * counts["vaccine_1"] / counts["rows"],
            "vaccination_unknown_percent": 100 * (counts["vaccine_missing"] + counts["vaccine_9"]) / counts["rows"],
        }
    return {
        "source": source.name, "sha256": fingerprint, "column_count": len(columns),
        "candidate_denominator_columns": [name for name in columns if any(
            term in name.upper() for term in ("LEITO", "CAPAC", "POPUL"))],
        "counts": {name: dict(counts) for name, counts in scopes.items()},
        "rates": rates, "icu_intervals_full_file": dict(icu),
        "vaccine_quality_full_file": dict(vaccine), "icu_hospital_cross_tab": dict(hospital_pairs),
        "limitations": [
            "Taxas descrevem registros de casos, não população geral ou capacidade de leitos.",
            "Ausência de vacinação não pode ser convertida em não vacinado.",
            "Intervalos completos não constituem censo hospitalar ou capacidade operacional.",
            "Datas de dose posteriores aos sintomas não permitem presumir proteção prévia.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    print(json.dumps(investigate(args.source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
