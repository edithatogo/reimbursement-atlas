# pyright: reportUnusedFunction=false
"""Optional FastAPI surface for local atlas exploration.

The API is intentionally read-only. It exposes seed metadata and generated
readiness artefacts, not live source fetching or restricted raw schedule dumps.
"""

from __future__ import annotations

from typing import Any

from reimburse_atlas.analysis import analysis_readiness_rows, source_readiness_rows
from reimburse_atlas.ingest import build_first_wave_ingestion_plan
from reimburse_atlas.registry import (
    load_analysis_catalogue,
    load_source_registry,
    load_source_status,
    load_source_versions,
)


def create_app() -> Any:
    """Create the optional FastAPI app.

    FastAPI is imported lazily so the core package remains usable in lightweight
    environments. Install the future `api` extra before running this surface.
    """
    try:
        from fastapi import FastAPI
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        msg = "Install the API extra before running the FastAPI app."
        raise RuntimeError(msg) from exc

    app = FastAPI(
        title="Reimbursement Atlas",
        version="0.1.0",
        description="Read-only seed API for public reimbursement source metadata.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sources")
    def sources() -> list[dict[str, Any]]:
        return [source.model_dump(mode="json") for source in load_source_registry()]

    @app.get("/analyses")
    def analyses() -> list[dict[str, Any]]:
        return [analysis.model_dump(mode="json") for analysis in load_analysis_catalogue()]

    @app.get("/source-status")
    def source_status() -> list[dict[str, Any]]:
        return [record.model_dump(mode="json") for record in load_source_status()]

    @app.get("/readiness/sources")
    def source_readiness() -> list[dict[str, object]]:
        return source_readiness_rows(load_source_registry())

    @app.get("/readiness/analyses")
    def analysis_readiness() -> list[dict[str, object]]:
        return analysis_readiness_rows(load_analysis_catalogue(), load_source_registry())

    @app.get("/ingestion/first-wave")
    def first_wave_ingestion() -> list[dict[str, Any]]:
        return [
            task.model_dump(mode="json")
            for task in build_first_wave_ingestion_plan(
                load_source_registry(),
                load_source_versions(),
            )
        ]

    return app


app = create_app
