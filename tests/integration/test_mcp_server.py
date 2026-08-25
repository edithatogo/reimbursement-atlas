"""MCP 2 public API integration tests."""

from __future__ import annotations

from typing import Any

import pytest

from reimburse_atlas.mcp_server import create_mcp_server

mcp = pytest.importorskip("mcp", reason="MCP optional dependency is not installed")


@pytest.mark.anyio
async def test_mcp_server_registers_read_only_tools() -> None:
    """The adapter should expose the documented tools through the MCP 2 API."""
    from mcp.server import MCPServer

    server = create_mcp_server()

    assert isinstance(server, MCPServer)
    assert {tool.name for tool in await server.list_tools()} == {
        "analysis_readiness",
        "first_wave_ingestion_plan",
        "list_analyses",
        "list_sources",
        "source_readiness",
        "source_status",
    }


@pytest.mark.parametrize(
    "tool_name",
    [
        "analysis_readiness",
        "first_wave_ingestion_plan",
        "list_analyses",
        "list_sources",
        "source_readiness",
        "source_status",
    ],
)
@pytest.mark.anyio
async def test_mcp_server_tools_are_callable_without_mutation(tool_name: str) -> None:
    """Every registered tool should return structured metadata without arguments."""
    result: Any = await create_mcp_server().call_tool(tool_name, {})

    assert result.is_error is False
    assert result.structured_content is not None
