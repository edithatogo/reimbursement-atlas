# ADR 0007: Read-only interfaces first

Date: 2026-07-03

## Status

Accepted.

## Context

The atlas may eventually support a CLI, API and MCP server. Write operations, live fetching and ontology-backed mapping can create data-governance and licensing risks.

## Decision

Expose only read-only interfaces until source acquisition, licence gates and provenance logging are production-ready. CLI commands can generate local derived artefacts from fixtures. API and MCP surfaces should return registry/readiness/plan data and generated local artefacts only.

## Consequences

- Safer public repository and future Hugging Face dataset.
- Easier use by future agents without accidental live scraping.
- API/MCP implementation can progress without committing to live data acquisition semantics.
