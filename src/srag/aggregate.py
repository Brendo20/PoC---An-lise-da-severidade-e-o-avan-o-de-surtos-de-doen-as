"""Snapshot agregado para validar o frontend local; não constitui publicação nem carga SQL."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from srag.profile import normalize_code, parse_date

VERSION = "1.0.0"
METRIC_VERSION = "0.2.0"
MIN_COUNT = 5
SOURCE_URL = "https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/d96d6348-083a-4184-a39a-794b5e8ec337"
STATES = (
    ("11", "RO", "Rondônia", "Norte"), ("12", "AC", "Acre", "Norte"),
    ("13", "AM", "Amazonas", "Norte"), ("14", "RR", "Roraima", "Norte"),
    ("15", "PA", "Pará", "Norte"), ("16", "AP", "Amapá", "Norte"),
    ("17", "TO", "Tocantins", "Norte"), ("21", "MA", "Maranhão", "Nordeste"),
    ("22", "PI", "Piauí", "Nordeste"), ("23", "CE", "Ceará", "Nordeste"),
    ("24", "RN", "Rio Grande do Norte", "Nordeste"), ("25", "PB", "Paraíba", "Nordeste"),
    ("26", "PE", "Pernambuco", "Nordeste"), ("27", "AL", "Alagoas", "Nordeste"),
    ("28", "SE", "Sergipe", "Nordeste"), ("29", "BA", "Bahia", "Nordeste"),
    ("31", "MG", "Minas Gerais", "Sudeste"), ("32", "ES", "Espírito Santo", "Sudeste"),
    ("33", "RJ", "Rio de Janeiro", "Sudeste"), ("35", "SP", "São Paulo", "Sudeste"),
    ("41", "PR", "Paraná", "Sul"), ("42", "SC", "Santa Catarina", "Sul"),
    ("43", "RS", "Rio Grande do Sul", "Sul"), ("50", "MS", "Mato Grosso do Sul", "Centro-Oeste"),
    ("51", "MT", "Mato Grosso", "Centro-Oeste"), ("52", "GO", "Goiás", "Centro-Oeste"),
    ("53", "DF", "Distrito Federal", "Centro-Oeste"),
)
BY_UF = {item[1]: item for item in STATES}
REGIONS = ("Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste")


def shift_month(month: date, offset: int) -> date:
    index = month.year * 12 + month.month - 1 + offset
    year, zero_month = divmod(index, 12)
    return date(year, zero_month + 1, 1)


def count_result(value: int) -> dict:
    if 0 < value < MIN_COUNT:
        return {"value": None, "status": "suppressed"}
    return {"value": value, "status": "available"}


def unavailable(reason: str) -> dict:
    return {"value": None, "status": "unavailable", "reason": reason}


def percentage(numerator: int, denominator: int, unknown: int = 0) -> dict:
    if denominator == 0:
        return unavailable("zero_denominator")
    if any(0 < v < MIN_COUNT for v in (numerator, denominator - numerator, unknown)):
        return {"value": None, "status": "suppressed", "reason": "small_category"}
    return {"value": numerator / denominator * 100, "status": "available",
            "numerator": numerator, "denominator": denominator, "unknown": unknown,
            "unknown_percent": unknown / (denominator + unknown) * 100}


def growth(current: int, previous: int) -> dict:
    if previous == 0:
        return unavailable("zero_denominator")
    if any(0 < v < MIN_COUNT for v in (current, previous)):
        return {"value": None, "status": "suppressed", "reason": "small_category"}
    return {"value": (current / previous - 1) * 100, "status": "available",
            "numerator": current, "denominator": previous}


def build_snapshot(source: Path, *, reference: date, coverage_start: date,
                   coverage_end: date) -> dict:
    if not coverage_start <= reference <= coverage_end:
        raise ValueError("Referência deve estar dentro da cobertura declarada")
    start_month = shift_month(reference.replace(day=1), -11)
    daily_start = reference - timedelta(days=29)
    previous_start = reference - timedelta(days=13)
    current_start = reference - timedelta(days=6)
    schema = {"DT_SIN_PRI", "SG_UF", "EVOLUCAO", "UTI", "VACINA"}
    dates = defaultdict(Counter)
    categories = defaultdict(lambda: defaultdict(Counter))
    issues = Counter()
    with source.open("rb") as stream:
        fingerprint = hashlib.file_digest(stream, "sha256").hexdigest()
    rows = 0
    valid = 0
    in_window = 0
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";", strict=True)
        columns = reader.fieldnames or []
        if not schema <= set(columns) or len(columns) != len(set(columns)):
            raise ValueError("Esquema CSV incompatível com agregações SRAG")
        for row in reader:
            rows += 1
            if None in row or any(v is None for v in row.values()):
                issues["malformed_rows"] += 1
                continue
            try:
                symptom_date = parse_date(row["DT_SIN_PRI"])
            except ValueError:
                issues["invalid_symptom_date"] += 1
                continue
            if symptom_date is None:
                issues["missing_symptom_date"] += 1
                continue
            if not coverage_start <= symptom_date <= coverage_end:
                issues["outside_declared_coverage"] += 1
                continue
            if symptom_date > reference:
                issues["after_reference"] += 1
                continue
            valid += 1
            uf = row["SG_UF"].strip().upper()
            territories = ["Brasil"]
            if uf in BY_UF:
                territories.extend((uf, BY_UF[uf][3]))
            else:
                issues["unknown_residence_uf"] += 1
            for territory in territories:
                dates[territory][symptom_date] += 1
            if symptom_date < start_month:
                continue
            in_window += 1
            for territory in territories:
                for field in ("EVOLUCAO", "UTI", "VACINA"):
                    categories[territory][field][normalize_code(row[field])] += 1
    if not rows or not valid:
        raise ValueError("CSV sem casos válidos na cobertura e referência declaradas")
    # Impedir associar agregações a hash de arquivo modificado durante a leitura.
    with source.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != fingerprint:
            raise ValueError("Arquivo de origem mudou durante o processamento")

    def covered(start: date, end: date) -> bool:
        return coverage_start <= start <= end <= coverage_end

    def series_point(counts: Counter, start: date, end: date) -> dict:
        result = count_result(sum(n for d, n in counts.items() if start <= d <= end))
        if not covered(start, end):
            result = unavailable("outside_coverage")
        return {"date": start.isoformat(), **result}

    territories = {}
    for territory in ("Brasil", *BY_UF, *REGIONS):
        counts = dates[territory]
        total = sum(n for d, n in counts.items() if start_month <= d <= reference)
        outcome = categories[territory]["EVOLUCAO"]
        icu = categories[territory]["UTI"]
        vaccine = categories[territory]["VACINA"]
        known = sum(outcome[c] for c in ("1", "2", "3"))
        metrics = {
            "cases": count_result(total),
            "growth": growth(sum(n for d, n in counts.items() if current_start <= d <= reference),
                             sum(n for d, n in counts.items() if previous_start <= d < current_start)),
            "fatality": percentage(outcome["2"], known, total - known),
            "icu_admission": percentage(icu["1"], icu["1"] + icu["2"], total - icu["1"] - icu["2"]),
            "flu_vaccination_cases": percentage(vaccine["1"], vaccine["1"] + vaccine["2"],
                                                total - vaccine["1"] - vaccine["2"]),
            "icu_occupancy": unavailable("missing_bed_source"),
            "population_vaccination": unavailable("missing_population_source"),
        }
        if not covered(previous_start, reference):
            metrics["growth"] = unavailable("outside_coverage")
        if not covered(start_month, reference):
            for key in ("cases", "fatality", "icu_admission", "flu_vaccination_cases"):
                metrics[key] = unavailable("outside_coverage")
        daily = [series_point(counts, daily_start + timedelta(days=i), daily_start + timedelta(days=i))
                 for i in range(30)]
        monthly = []
        for i in range(12):
            month = shift_month(start_month, i)
            end = min(shift_month(month, 1) - timedelta(days=1), reference)
            monthly.append({**series_point(counts, month, end),
                            "partial": end < shift_month(month, 1) - timedelta(days=1)})
        territories[territory] = {"metrics": metrics, "daily": daily, "monthly": monthly}
    parameters = {"source_sha256": fingerprint, "reference": reference.isoformat(),
                  "coverage_start": coverage_start.isoformat(), "coverage_end": coverage_end.isoformat(),
                  "schema_version": VERSION, "metric_version": METRIC_VERSION, "minimum_count": MIN_COUNT}
    identity = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "schema_version": VERSION, "metric_version": METRIC_VERSION,
        "snapshot_id": f"srag-{identity}-{reference.isoformat()}-v{VERSION}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reference": reference.isoformat(), "window_start": start_month.isoformat(),
        "coverage": {"start": coverage_start.isoformat(), "end": coverage_end.isoformat(),
                     "basis": "declared_source_extract_not_completeness_guarantee"},
        "source": {"filename": source.name, "url": SOURCE_URL, "sha256": fingerprint},
        "database_load": {"status": "not_loaded", "loaded_at": None},
        "audit": {"input_rows": rows, "valid_through_reference": valid,
                  "cases_in_window": in_window, "issues": dict(issues)},
        "privacy": {"minimum_count": MIN_COUNT, "audience": "local_development_only",
                    "policy": "primary_suppression_not_safe_for_publication",
                    "warning": "Publicação exige avaliar inferência e supressão complementar."},
        "states": [{"code": c, "id": uf, "name": n, "region": r} for c, uf, n, r in STATES],
        "regions": list(REGIONS), "territories": territories,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--reference", required=True, type=date.fromisoformat)
    parser.add_argument("--coverage-start", required=True, type=date.fromisoformat)
    parser.add_argument("--coverage-end", required=True, type=date.fromisoformat)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.source.resolve():
        parser.error("Saída deve ser nova e diferente da origem")
    result = build_snapshot(args.source, reference=args.reference,
                            coverage_start=args.coverage_start, coverage_end=args.coverage_end)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")
    print(f"Snapshot local criado: {result['audit']['input_rows']} registros; {args.output}")


if __name__ == "__main__":
    main()
