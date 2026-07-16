"""Smoke tests for the optional read-only FastAPI surface."""

from __future__ import annotations

import pytest


def _client():
    """Build a client only when the optional API environment is installed."""
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from reimburse_atlas.api import create_app

    return TestClient(create_app())


def test_read_only_api_routes_return_seed_payloads() -> None:
    """The optional API should serve local metadata without network mutation."""
    client = _client()

    assert client.get("/health").json() == {"status": "ok"}
    assert len(client.get("/sources").json()) >= 50
    assert len(client.get("/analyses").json()) >= 20
    assert client.get("/readiness/sources").json()
    assert client.get("/readiness/analyses").json()
    assert client.get("/ingestion/first-wave").json()


def test_api_exposes_no_mutating_routes() -> None:
    """The API contract must remain read-only until separately designed."""
    pytest.importorskip("fastapi")
    from reimburse_atlas.api import create_app

    app = create_app()
    mutating_methods = {"POST", "PUT", "PATCH", "DELETE"}
    assert not any(
        route.methods.intersection(mutating_methods)
        for route in app.routes
        if hasattr(route, "methods")
    )
