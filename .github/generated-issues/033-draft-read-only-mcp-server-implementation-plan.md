# Draft read-only MCP server implementation plan

Epic: `IFACE-001` — Read-only interfaces

Labels: type:mcp, phase:2-expansion, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] A lazy optional MCP server exposes read-only source, analysis, readiness, and ingestion-plan resources.
- [x] `mcp/tools.seed.json` and `docs/API_MCP_CLI_PLAN.md` document the read-only tool boundary and no-live-fetch policy.
- [x] The optional interface module is import-tested without requiring the MCP SDK in the default environment.
