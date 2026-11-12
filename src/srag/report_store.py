"""Arquivos privados de relatório e auditoria, sem conteúdo de raciocínio do modelo."""
from __future__ import annotations

import json
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from srag.aggregate import BY_UF
from srag.database import TERRITORIES
from srag.groq_client import GroqClient
from srag.agent import ReportAgent
from srag.news import NewsSearch


class ReportError(RuntimeError):
    def __init__(self, code: str, status: int):
        super().__init__(code)
        self.code, self.status = code, status


class ReportStore:
    def __init__(self, root: Path):
        self.root = root

    def folder(self, identifier: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{32}", identifier):
            raise FileNotFoundError("report_not_found")
        return self.root / identifier

    def start(self) -> tuple[str, list, object]:
        identifier = uuid4().hex
        directory = self.folder(identifier)
        directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        events = []

        def emit(event, **fields):
            record = {"at": datetime.now(timezone.utc).isoformat(), "event": event, **fields}
            with (directory / "audit.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            events.append(record)

        return identifier, events, emit

    def save(self, report: dict, html: str):
        directory = self.folder(report["report_id"])
        (directory / "report.html").write_text(html, encoding="utf-8")
        # JSON por último sinaliza relatório finalizado para leitura.
        with (directory / "report.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)

    def read(self, identifier: str) -> dict:
        return json.loads((self.folder(identifier) / "report.json").read_text(encoding="utf-8"))

    def html(self, identifier: str) -> str:
        self.read(identifier)
        return (self.folder(identifier) / "report.html").read_text(encoding="utf-8")


class ReportService:
    def __init__(self, repository, store: ReportStore, client=None, news_search=None, clock=None):
        self.repository, self.store = repository, store
        self.client = client if client is not None else GroqClient()
        self.news_search = news_search if news_search is not None else NewsSearch()
        self.clock = clock or time.monotonic
        self.lock = threading.Lock()
        self.cache = {}
        self.last_started = float("-inf")

    def status(self) -> dict:
        return {"configured": self.client.configured, "provider": "groq", "model": self.client.model}

    def generate(self, territories: list[str], expected_snapshot: str) -> dict:
        if (not isinstance(territories, list) or not 1 <= len(territories) <= 2
                or any(item not in TERRITORIES for item in territories) or len(set(territories)) != len(territories)):
            raise ReportError("invalid_territories", 400)
        if len(territories) == 2 and ("Brasil" in territories or
                ((territories[0] in BY_UF) != (territories[1] in BY_UF))):
            raise ReportError("incompatible_comparison", 400)
        if not self.client.configured:
            raise ReportError("provider_not_configured", 503)
        if not self.lock.acquire(blocking=False):
            raise ReportError("generation_in_progress", 429)
        try:
            snapshot = self.repository.pin_snapshot()
            if snapshot["snapshot_id"] != expected_snapshot:
                raise ReportError("snapshot_changed_refresh_dashboard", 409)
            key = (expected_snapshot, tuple(territories), self.client.model)
            cached = self.cache.get(key)
            if cached and self.clock() - cached[0] < 300:
                return {**self.store.read(cached[1]), "cached": True}
            if self.clock() - self.last_started < 60:
                raise ReportError("generation_cooldown", 429)
            identifier, events, emit = self.store.start()
            self.last_started = self.clock()
            emit("report_started", snapshot_id=expected_snapshot, territories=territories, model=self.client.model)
            try:
                result = ReportAgent(self.repository, self.client, self.news_search).run(snapshot, territories, emit)
                emit("report_validated", status=result["status"], warnings=result["warnings"])
                result.update(report_id=identifier, audit=events.copy(), cached=False)
                from srag.report_html import render_report
                self.store.save(result, render_report(result))
                emit("report_saved", report_id=identifier)
                if result["status"] == "complete":
                    if len(self.cache) >= 100:
                        self.cache.clear()
                    self.cache[key] = (self.clock(), identifier)
                return result
            except Exception as error:
                emit("report_failed", error_type=type(error).__name__)
                raise
        finally:
            self.lock.release()
