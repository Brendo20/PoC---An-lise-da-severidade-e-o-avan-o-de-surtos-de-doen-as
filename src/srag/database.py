"""Persistência PostgreSQL de agregações versionadas; nenhuma linha de paciente."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from copy import deepcopy
from pathlib import Path

from srag.aggregate import BY_UF, REGIONS

TERRITORIES = frozenset(("Brasil", *BY_UF, *REGIONS))
MIGRATION = Path(__file__).resolve().parents[2] / "sql" / "001_aggregate_store.sql"


def connect(env_name: str):
    dsn = os.environ.get(env_name)
    if not dsn:
        raise RuntimeError(f"Configure {env_name} no ambiente local; não envie credenciais no chat")
    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError('Instale o extra PostgreSQL: pip install -e ".[postgres]"') from error
    return psycopg.connect(dsn, connect_timeout=5, application_name="indicium-srag")


def validate_snapshot(snapshot: dict) -> None:
    if snapshot.get("schema_version") != "1.0.0":
        raise ValueError("Versão de snapshot incompatível")
    if set(snapshot.get("territories", {})) != TERRITORIES:
        raise ValueError("Snapshot deve conter Brasil, 27 UFs e cinco regiões")
    if not re.fullmatch(r"[a-f0-9]{64}", snapshot.get("source", {}).get("sha256", "")):
        raise ValueError("SHA-256 de origem inválido")
    if snapshot.get("reference") != "2019-12-28":
        raise ValueError("Esta PoC está fixada na referência histórica 28/12/2019")
    if snapshot.get("privacy", {}).get("audience") != "local_development_only":
        raise ValueError("Snapshot deve manter a classificação de uso restrito local")
    for document in snapshot["territories"].values():
        if len(document.get("daily", [])) != 30 or len(document.get("monthly", [])) != 12:
            raise ValueError("Séries devem conter 30 dias e 12 meses")
        for metric in ("icu_occupancy", "population_vaccination"):
            if document["metrics"][metric].get("value") is not None:
                raise ValueError("Indicador sem denominador não pode receber valor")


def content_hash(snapshot: dict) -> str:
    content = deepcopy(snapshot)
    content.pop("generated_at", None)
    content.pop("database_load", None)
    encoded = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def load_snapshot(connection, snapshot: dict) -> dict:
    """Carga atômica; id repetido só é aceito se o conteúdo analítico for idêntico."""
    validate_snapshot(snapshot)
    identifier = snapshot["snapshot_id"]
    checksum = content_hash(snapshot)
    metadata = {key: value for key, value in snapshot.items() if key != "territories"}
    with connection.transaction():
        # Serializa a troca da carga ativa; não mantém estado parcial em caso de falha.
        connection.execute("SELECT pg_advisory_xact_lock(843211, 1)")
        existing = connection.execute(
            "SELECT content_hash, loaded_at FROM srag.snapshots WHERE snapshot_id = %s",
            (identifier,),
        ).fetchone()
        if existing and existing[0] != checksum:
            raise ValueError("Identificador de snapshot já existe com conteúdo diferente")
        if not existing:
            inserted = connection.execute(
                """INSERT INTO srag.snapshots
                   (snapshot_id, content_hash, source_hash, reference_date, metadata)
                   VALUES (%s, %s, %s, %s, %s::jsonb) RETURNING loaded_at""",
                (identifier, checksum, snapshot["source"]["sha256"], snapshot["reference"],
                 json.dumps(metadata, ensure_ascii=False)),
            ).fetchone()
            loaded_at = inserted[0]
            for territory, document in snapshot["territories"].items():
                connection.execute(
                    """INSERT INTO srag.territory_aggregates(snapshot_id, territory, document)
                       VALUES (%s, %s, %s::jsonb)""",
                    (identifier, territory, json.dumps(document, ensure_ascii=False)),
                )
        else:
            loaded_at = existing[1]
        connection.execute(
            """INSERT INTO srag.active_snapshot(singleton, snapshot_id) VALUES (true, %s)
               ON CONFLICT (singleton) DO UPDATE SET snapshot_id = EXCLUDED.snapshot_id""",
            (identifier,),
        )
    return {"snapshot_id": identifier, "loaded_at": loaded_at.isoformat(),
            "status": "already_loaded" if existing else "loaded"}


class PostgresRepository:
    """Interface de ferramenta restrita: snapshot fixado e território em allowlist."""

    def __init__(self, connection_factory=None):
        self.connection_factory = connection_factory or (lambda: connect("SRAG_DATABASE_URL"))

    def dashboard(self) -> dict:
        """Uma instrução SELECT fixa a carga ativa para todo o dashboard."""
        with self.connection_factory() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '5s'")
            rows = connection.execute(
                """SELECT s.snapshot_id, s.loaded_at, s.metadata, t.territory, t.document
                   FROM srag.active_snapshot a
                   JOIN srag.snapshots s ON s.snapshot_id = a.snapshot_id
                   JOIN srag.territory_aggregates t ON t.snapshot_id = s.snapshot_id
                   WHERE a.singleton = true ORDER BY t.territory"""
            ).fetchall()
        if not rows:
            raise LookupError("Nenhuma carga ativa disponível")
        if len(rows) != len(TERRITORIES) or {row[3] for row in rows} != TERRITORIES:
            raise LookupError("Carga incompleta: territórios esperados não encontrados")
        first = rows[0]
        if any(row[0] != first[0] for row in rows):
            raise LookupError("Resposta contém versões diferentes de carga")
        result = deepcopy(first[2])
        result["snapshot_id"] = first[0]
        result["database_load"] = {"status": "loaded", "loaded_at": first[1].isoformat()}
        result["territories"] = {row[3]: row[4] for row in rows}
        return result

    def pin_snapshot(self) -> dict:
        with self.connection_factory() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '5s'")
            row = connection.execute(
                """SELECT s.snapshot_id, s.loaded_at, s.metadata
                   FROM srag.snapshots s JOIN srag.active_snapshot a
                   ON s.snapshot_id = a.snapshot_id WHERE a.singleton = true"""
            ).fetchone()
        if not row:
            raise LookupError("Nenhuma carga ativa; execute a ingestão antes do relatório")
        return {"snapshot_id": row[0], "loaded_at": row[1].isoformat(), "metadata": row[2]}

    def territory(self, snapshot_id: str, territory: str) -> dict:
        if territory not in TERRITORIES:
            raise ValueError("Território não permitido")
        if not isinstance(snapshot_id, str) or not 1 <= len(snapshot_id) <= 160:
            raise ValueError("Identificador de snapshot inválido")
        with self.connection_factory() as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '5s'")
            row = connection.execute(
                """SELECT document FROM srag.territory_aggregates
                   WHERE snapshot_id = %s AND territory = %s""",
                (snapshot_id, territory),
            ).fetchone()
        if not row:
            raise LookupError("Território não encontrado nesta carga")
        return row[0]

    def metrics(self, snapshot_id: str, territory: str) -> dict:
        result = self.territory(snapshot_id, territory)["metrics"]
        # Indicadores auxiliares não são expostos como atendimento ao enunciado.
        return {key: result[key] for key in (
            "cases", "growth", "fatality", "icu_admission", "flu_vaccination_cases",
            "icu_occupancy", "population_vaccination")}

    def series(self, snapshot_id: str, territory: str) -> dict:
        result = self.territory(snapshot_id, territory)
        return {key: result[key] for key in ("daily", "monthly")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate")
    loader = sub.add_parser("load")
    loader.add_argument("snapshot", type=Path)
    sub.add_parser("status")
    args = parser.parse_args()
    if args.command == "status":
        result = PostgresRepository().pin_snapshot()
        print(json.dumps({key: result[key] for key in ("snapshot_id", "loaded_at")}))
        return
    with connect("SRAG_LOADER_DATABASE_URL") as connection:
        if args.command == "migrate":
            connection.execute(MIGRATION.read_text(encoding="utf-8"))
            print("Migração 001 aplicada no banco configurado")
        else:
            result = load_snapshot(connection, json.loads(args.snapshot.read_text(encoding="utf-8")))
            print(json.dumps(result))


if __name__ == "__main__":
    main()
