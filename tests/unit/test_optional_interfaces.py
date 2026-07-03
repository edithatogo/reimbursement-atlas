"""Tests for optional API and MCP interface modules."""

from __future__ import annotations

from reimburse_atlas import api, mcp_server


def test_api_module_is_lazy_importable() -> None:
    """The API module should import without FastAPI installed."""
    assert callable(api.create_app)


def test_mcp_module_is_lazy_importable() -> None:
    """The MCP module should import without the MCP SDK installed."""
    assert callable(mcp_server.create_mcp_server)
