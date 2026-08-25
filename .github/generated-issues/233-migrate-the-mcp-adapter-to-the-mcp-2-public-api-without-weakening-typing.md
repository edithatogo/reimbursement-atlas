# Migrate the MCP adapter to the MCP 2 public API without weakening typing

Epic: `MCP2-001` — MCP 2 typed API migration

Labels: type:runtime, type:refactor, type:mcp, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] MCP 2 replaces every removed mcp.server.fastmcp dependency with supported public APIs.
- [x] BasedPyright remains at zero errors without suppressions or relaxed settings.
- [x] MCP behavior, Python 3.14, security and deterministic-generation gates pass.
- [x] MCP Python SDK 2.1.1 exports the supported typed mcp.server.MCPServer replacement.
- [x] The adapter, behavior tests, strict BasedPyright and full local quality gates pass without suppressions or compatibility shims.
