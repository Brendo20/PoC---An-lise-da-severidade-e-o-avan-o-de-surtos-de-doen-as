"""Diagnóstico agregado do CSV original; não exporta registros ou identificadores."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

VERSION = "1.0.0"
DATE_FIELDS = ("DT_SIN_PRI", "DT_NOTIFIC", "DT_INTERNA", "DT_ENTUTI", "DT_SAIDUTI", "DT_EVOLUCA")
CODE_FIELDS = {
    "UTI": {"1", "2", "9"},
    "EVOLUCAO": {"1", "2", "3", "9"},
    "VACINA": {"1", "2", "9"},
    "HOSPITAL": {"1", "2", "9"},
}
REQUIRED = {"NU_NOTIFIC", *DATE_FIELDS, *CODE_FIELDS}


def normalize_code(value: str) -> str:
    """Aceita códigos inteiros e representação decimal inteira; mantém outros inválidos."""
    value = value.strip()
    if value.endswith(".0") and value[:-2].isdigit():
        return value[:-2]
    return value


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    if "T" in value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            raise ValueError("Timestamp ISO inválido") from None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Formato de data não suportado")


def profile_csv(source: Path, *, as_of: date, source_url: str) -> dict:
    """Retorna evidências agregadas. Datas futuras não definem a referência analítica."""
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    file_hash = digest.hexdigest()
    date_stats = {field: {"missing": 0, "invalid": 0, "future": 0, "min": None,
                          "max": None, "latest_not_future": None} for field in DATE_FIELDS}
    codes = {field: Counter() for field in CODE_FIELDS}
    issues = Counter()
    seen_ids = set()
    daily = Counter()
    rows = 0
    malformed = 0
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";", strict=True)
        columns = reader.fieldnames or []
        if len(set(columns)) != len(columns):
            raise ValueError("Cabeçalho com colunas duplicadas")
        missing = REQUIRED - set(columns)
        if missing:
            raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
        for row in reader:
            rows += 1
            if None in row or any(value is None for value in row.values()):
                malformed += 1
                continue
            ident = row["NU_NOTIFIC"].strip()
            if not ident:
                issues["missing_notification_id"] += 1
            else:
                # Identificadores só são mantidos como hashes, nunca incluídos no resultado.
                ident_hash = hashlib.sha256(ident.encode()).digest()
                if ident_hash in seen_ids:
                    issues["repeated_notification_id"] += 1
                seen_ids.add(ident_hash)
            parsed = {}
            for field, stats in date_stats.items():
                try:
                    value = parse_date(row[field])
                except ValueError:
                    stats["invalid"] += 1
                    parsed[field] = None
                    continue
                parsed[field] = value
                if value is None:
                    stats["missing"] += 1
                    continue
                iso = value.isoformat()
                stats["min"] = min(stats["min"] or iso, iso)
                stats["max"] = max(stats["max"] or iso, iso)
                if value > as_of:
                    stats["future"] += 1
                else:
                    stats["latest_not_future"] = max(stats["latest_not_future"] or iso, iso)
                if field == "DT_SIN_PRI" and value <= as_of:
                    daily[iso] += 1
            for field, allowed in CODE_FIELDS.items():
                value = normalize_code(row[field])
                label = value if value in allowed else ("missing" if not value else "invalid")
                codes[field][label] += 1
            for earlier, later, label in (
                ("DT_SIN_PRI", "DT_NOTIFIC", "notification_before_symptoms"),
                ("DT_SIN_PRI", "DT_INTERNA", "admission_before_symptoms"),
                ("DT_SIN_PRI", "DT_ENTUTI", "icu_before_symptoms"),
                ("DT_ENTUTI", "DT_SAIDUTI", "icu_exit_before_entry"),
                ("DT_SIN_PRI", "DT_EVOLUCA", "outcome_before_symptoms"),
            ):
                if parsed[earlier] and parsed[later] and parsed[later] < parsed[earlier]:
                    issues[label] += 1
            if normalize_code(row["UTI"]) == "1":
                for field in ("DT_ENTUTI", "DT_SAIDUTI"):
                    if not parsed[field]:
                        issues["icu_yes_without_valid_" + field.lower()] += 1
            elif row["DT_ENTUTI"].strip() or row["DT_SAIDUTI"].strip():
                issues["icu_dates_without_yes"] += 1
    if not rows or not daily:
        raise ValueError("Arquivo sem registros com início de sintomas válido até a data de corte")
    return {
        "profile_version": VERSION,
        "analysis_id": f"profile-{file_hash[:16]}-{as_of.isoformat()}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of": as_of.isoformat(),
        "source": {"filename": source.name, "url": source_url, "sha256": file_hash,
                   "bytes": source.stat().st_size},
        "database_load": {"status": "not_loaded", "loaded_at": None},
        "rows": rows,
        "malformed_rows": malformed,
        "column_count": len(columns),
        "dates": date_stats,
        "codes": {field: dict(sorted(values.items())) for field, values in codes.items()},
        "issues": dict(sorted(issues.items())),
        "analytical_reference_candidate": max(daily),
        "limitations": [
            "Referência candidata exige revisão de plausibilidade e cobertura.",
            "Identificadores repetidos não equivalem automaticamente a duplicatas clínicas.",
            "Datas ausentes de UTI não permitem reconstruir ocupação de leitos.",
            "Este diagnóstico não constitui uma carga no banco ou liberação de dados públicos.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("Saída não pode substituir o CSV original")
    if args.output.exists():
        parser.error("Saída já existe; use outro nome para preservar a evidência anterior")
    report = profile_csv(args.source, as_of=args.as_of, source_url=args.source_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"Diagnóstico concluído: {report['rows']} registros; saída: {args.output}")


if __name__ == "__main__":
    main()
