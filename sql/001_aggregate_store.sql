-- Aplicar apenas no banco exclusivo da PoC, com seu proprietário.
-- Não cria outro servidor PostgreSQL nem altera bancos dos portais.
CREATE SCHEMA IF NOT EXISTS srag;
REVOKE ALL ON SCHEMA srag FROM PUBLIC;

CREATE TABLE IF NOT EXISTS srag.schema_versions (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS srag.snapshots (
    snapshot_id text PRIMARY KEY,
    content_hash text NOT NULL CHECK (content_hash ~ '^[a-f0-9]{64}$'),
    source_hash text NOT NULL CHECK (source_hash ~ '^[a-f0-9]{64}$'),
    reference_date date NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    metadata jsonb NOT NULL CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE TABLE IF NOT EXISTS srag.territory_aggregates (
    snapshot_id text NOT NULL REFERENCES srag.snapshots(snapshot_id),
    territory text NOT NULL,
    document jsonb NOT NULL CHECK (jsonb_typeof(document) = 'object'),
    PRIMARY KEY (snapshot_id, territory)
);

CREATE TABLE IF NOT EXISTS srag.active_snapshot (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    snapshot_id text NOT NULL REFERENCES srag.snapshots(snapshot_id)
);

REVOKE ALL ON ALL TABLES IN SCHEMA srag FROM PUBLIC;
INSERT INTO srag.schema_versions(version) VALUES (1) ON CONFLICT DO NOTHING;

-- Conceder somente aos logins exclusivos previamente provisionados:
-- GRANT USAGE ON SCHEMA srag TO srag_reader;
-- GRANT SELECT ON srag.snapshots, srag.territory_aggregates, srag.active_snapshot
--     TO srag_reader;
-- O loader usa um login distinto com privilégios de carga neste banco.
