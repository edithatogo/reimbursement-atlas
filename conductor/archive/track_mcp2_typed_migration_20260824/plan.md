# Plan

- [x] Record the MCP 1.x compatibility boundary and failing MCP 2 type diagnostics. Upstream replacement verified in MCP 2.1.1.
- [x] Add contract tests for current MCP tools and transport behavior. (`ffc0411c`)
- [x] Implement the MCP 2 public server API adapter without type suppressions. (`ffc0411c`)
- [x] Run Ruff, BasedPyright, Python 3.14, unit, integration, and security gates. Local quality 27/27 passed.
- [x] Regenerate lockfile-derived SBOM, licence, readiness, package, dashboard, and handoff artifacts.
- [x] Run deterministic regeneration and automated review.
- [x] Prepare the validated migration for the protected workflow and archive only after every acceptance criterion passes.

## Review Fixes

- [x] Guard the optional integration shard on `mcp.server`, not the repository's `mcp/` namespace directory. (`cf2586b5`)
