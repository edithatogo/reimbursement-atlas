# MCP 2 typed migration

## Overview

Migrate the optional MCP server from MCP Python SDK 1.x to 2.x without weakening static typing, runtime validation, or the stable evidence-core contracts.

## Requirements

- Replace removed `mcp.server.fastmcp` APIs with supported MCP 2 server interfaces.
- Preserve the existing CLI and MCP tool behavior or document intentional versioned changes.
- Keep BasedPyright at zero errors and retain strict project settings.
- Cover server construction, tool registration, requests, error handling, and shutdown with unit and integration tests.
- Regenerate lockfile, SBOM, licence, readiness, package, dashboard, and handoff evidence after migration.

## Acceptance criteria

- The `mcp` dependency permits MCP 2 and the lock resolves without the legacy 1.x SDK.
- No source imports `mcp.server.fastmcp`.
- BasedPyright, Ruff, Python 3.14 tests, MCP integration tests, security gates, and deterministic regeneration pass.
- Generated GitHub issue and Project artifacts identify this track and its migration dependency.

## Non-functional constraints

- Do not suppress, ignore, or downgrade type errors to enable the migration.
- Do not change evidence schemas or expose restricted data through MCP tools.
- Preserve least-privilege and local-only defaults.

## External gates

- MCP 2 upstream API and typing must be sufficiently stable for the project adapter.

## Out of scope

- Weakening typing or retaining compatibility shims that depend on removed private APIs.
- Publishing raw or restricted source payloads.

## Authoritative inputs

- `pyproject.toml`
- `src/reimburse_atlas/mcp_server.py`
- MCP Python SDK 2.x public API and type declarations at the selected pinned release.
