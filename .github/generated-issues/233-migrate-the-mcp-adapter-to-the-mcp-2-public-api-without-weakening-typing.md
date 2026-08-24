# Migrate the MCP adapter to the MCP 2 public API without weakening typing

Epic: `MCP2-001` — MCP 2 typed API migration

Labels: type:runtime, type:refactor, type:mcp, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] MCP 2 replaces every removed mcp.server.fastmcp dependency with supported public APIs.
- [ ] BasedPyright remains at zero errors without suppressions or relaxed settings.
- [ ] MCP behavior, Python 3.14, security and deterministic-generation gates pass.
- [ ] The current adapter requires a deliberate MCP 2 API and typing migration; a dependency-only update produces 16 type errors.
