# ADR 0024: Architecture boundaries as a generated quality gate

## Status
Accepted

## Context

The repo is growing across parsers, analysis, data-lake generation, dashboard, CLI, API/MCP and GitHub automation. Future contributors and agents need a way to detect architectural drift before it becomes hard to unwind.

## Decision

Add a static architecture-boundary scanner that maps internal imports onto a layered architecture and emits generated artefacts. The scanner checks that lower layers do not depend on higher layers and that internal import cycles are visible.

## Consequences

- Architecture policy is inspectable in code, CSV, JSONL and dashboard views.
- Intentional boundary changes require updating the layer map and documenting the reason.
- The gate is lightweight and does not replace full import-linter tooling, but it provides fast CI/CD feedback.
