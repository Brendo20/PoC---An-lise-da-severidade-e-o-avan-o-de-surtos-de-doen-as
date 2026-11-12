"""Servidor local de teste: fixture em memória, SEM conexão PostgreSQL."""
import json
from copy import deepcopy
from pathlib import Path

import uvicorn

from srag.api import create_app


class FixtureRepository:
    def __init__(self, snapshot):
        self.snapshot = deepcopy(snapshot)
        self.snapshot["database_load"] = {"status": "loaded", "loaded_at": "2026-11-12T12:45:32.573171+00:00"}

    def dashboard(self):
        return deepcopy(self.snapshot)

    def pin_snapshot(self):
        return {"snapshot_id": self.snapshot["snapshot_id"],
                "loaded_at": self.snapshot["database_load"]["loaded_at"], "metadata": {}}

    def metrics(self, snapshot_id, territory):
        return self.snapshot["territories"][territory]["metrics"]

    def series(self, snapshot_id, territory):
        return {key: self.snapshot["territories"][territory][key] for key in ("daily", "monthly")}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "frontend/data/snapshot.json").read_text(encoding="utf-8"))
    uvicorn.run(create_app(FixtureRepository(data), root / "frontend"),
                host="127.0.0.1", port=8767, access_log=False)
