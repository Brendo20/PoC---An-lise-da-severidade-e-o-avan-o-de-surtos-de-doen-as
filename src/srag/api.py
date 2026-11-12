"""API interna de leitura e frontend; executar com uvicorn srag.api:app."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from srag.database import PostgresRepository, TERRITORIES
from srag.report_store import ReportError, ReportService, ReportStore

LOGGER = logging.getLogger("srag.api")
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    territories: list[str] = Field(min_length=1, max_length=2)
    snapshot_id: str = Field(min_length=1, max_length=160)


def create_app(repository=None, frontend: Path | None = FRONTEND, report_service=None) -> FastAPI:
    application = FastAPI(title="SRAG 2019", docs_url=None, redoc_url=None, openapi_url=None)
    repository = repository if repository is not None else PostgresRepository()
    reports = report_service if report_service is not None else ReportService(
        repository, ReportStore(Path(os.environ.get("SRAG_REPORT_DIR", "reports/generated"))))

    @application.middleware("http")
    async def headers(request: Request, call_next):
        request_id = str(uuid4())
        try:
            response = await call_next(request)
        except Exception as error:
            # Nunca logar str(error): drivers podem incluir detalhes de conexão.
            LOGGER.error("request_failed id=%s error_type=%s", request_id, type(error).__name__)
            response = JSONResponse({"error": "service_unavailable", "request_id": request_id}, status_code=503)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    def call(operation):
        try:
            return operation()
        except Exception as error:
            LOGGER.warning("storage_unavailable error_type=%s", type(error).__name__)
            raise HTTPException(status_code=503, detail="Dados temporariamente indisponíveis") from None

    def validate_territory(territory: str):
        if territory not in TERRITORIES:
            raise HTTPException(status_code=400, detail="Território não permitido")

    @application.get("/health/live")
    def live():
        return {"status": "ok"}

    @application.get("/health/ready")
    def ready():
        snapshot = call(repository.pin_snapshot)
        return {"status": "ready", "snapshot_id": snapshot["snapshot_id"], "loaded_at": snapshot["loaded_at"]}

    @application.get("/api/dashboard")
    def dashboard():
        return call(repository.dashboard)

    @application.get("/api/metrics")
    def metrics(territory: str = Query(default="Brasil", max_length=24)):
        validate_territory(territory)
        snapshot = call(repository.pin_snapshot)
        result = call(lambda: repository.metrics(snapshot["snapshot_id"], territory))
        return {"snapshot_id": snapshot["snapshot_id"], "loaded_at": snapshot["loaded_at"],
                "territory": territory, "metrics": result}

    @application.get("/api/series")
    def series(territory: str = Query(default="Brasil", max_length=24)):
        validate_territory(territory)
        snapshot = call(repository.pin_snapshot)
        result = call(lambda: repository.series(snapshot["snapshot_id"], territory))
        return {"snapshot_id": snapshot["snapshot_id"], "loaded_at": snapshot["loaded_at"],
                "territory": territory, **result}

    @application.get("/api/agent/status")
    def agent_status():
        return reports.status()

    @application.post("/api/reports")
    def generate_report(body: ReportRequest):
        try:
            return reports.generate(body.territories, body.snapshot_id)
        except ReportError as error:
            raise HTTPException(status_code=error.status, detail=error.code,
                                headers={"Retry-After": "60"} if error.status == 429 else None) from None
        except Exception as error:
            LOGGER.warning("report_failed error_type=%s", type(error).__name__)
            raise HTTPException(status_code=503, detail="report_generation_unavailable") from None

    @application.get("/api/reports/{identifier}")
    def read_report(identifier: str):
        try:
            return reports.store.read(identifier)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="report_not_found") from None

    @application.get("/api/reports/{identifier}/html", response_class=HTMLResponse)
    def report_html(identifier: str):
        try:
            result = reports.store.html(identifier)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="report_not_found") from None
        return HTMLResponse(result, headers={"Content-Security-Policy":
            "default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"})

    if frontend is not None and frontend.is_dir():
        @application.get("/", response_class=HTMLResponse)
        def index():
            html = (frontend / "index.html").read_text(encoding="utf-8")
            marker = 'name="srag-data-source" content="local"'
            if html.count(marker) != 1:
                raise RuntimeError("Configuração do frontend incompatível")
            return HTMLResponse(html.replace(marker, 'name="srag-data-source" content="api"'))

        @application.get("/app.js")
        def javascript():
            return FileResponse(frontend / "app.js", media_type="application/javascript")

        @application.get("/styles.css")
        def stylesheet():
            return FileResponse(frontend / "styles.css", media_type="text/css")

        # Não montar frontend/ inteiro: frontend/data/ nunca é servido pela API.
        application.mount("/assets", StaticFiles(directory=frontend / "assets"), name="assets")
        application.mount("/vendor", StaticFiles(directory=frontend / "vendor"), name="vendor")

    return application


app = create_app()
