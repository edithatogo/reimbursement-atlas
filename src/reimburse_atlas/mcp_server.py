# pyright: reportUnusedFunction=false
"""Optional read-only MCP server for atlas metadata.

This module is intentionally lazy: importing it does not require the MCP Python
SDK. Install the `mcp` extra before creating or running the server.
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


def create_mcp_server() -> Any:
    """Create a read-only MCP server exposing registry and planning resources."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        msg = "Install the MCP extra before running the atlas MCP server."
        raise RuntimeError(msg) from exc

    server = FastMCP("reimbursement-atlas")

    @server.tool()
    def list_sources() -> list[dict[str, Any]]:
        """List public reimbursement source metadata."""
        return [source.model_dump(mode="json") for source in load_source_registry()]

    @server.tool()
    def list_analyses() -> list[dict[str, Any]]:
        """List planned policy analyses."""
        return [analysis.model_dump(mode="json") for analysis in load_analysis_catalogue()]

    @server.tool()
    def source_status() -> list[dict[str, Any]]:
        """Return current source observations and recommended acquisition actions."""
        return [record.model_dump(mode="json") for record in load_source_status()]

    @server.tool()
    def source_readiness() -> list[dict[str, object]]:
        """Return source-readiness score rows."""
        return source_readiness_rows(load_source_registry())

    @server.tool()
    def analysis_readiness() -> list[dict[str, object]]:
        """Return analysis-readiness score rows."""
        return analysis_readiness_rows(load_analysis_catalogue(), load_source_registry())

    @server.tool()
    def first_wave_ingestion_plan() -> list[dict[str, Any]]:
        """Return first-wave ingestion tasks without fetching live data."""
        return [
            task.model_dump(mode="json")
            for task in build_first_wave_ingestion_plan(
                load_source_registry(),
                load_source_versions(),
            )
        ]

    return server


def run() -> None:
    """Run the MCP server using the SDK default transport."""
    create_mcp_server().run()
