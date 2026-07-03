# ADR 0002: Analytical storage stack

## Status

Proposed.

## Context

The project needs fast local analytics, efficient columnar storage, SQL accessibility and semantic retrieval.

## Decision

Use Polars for transformations, Arrow/Parquet for snapshots, DuckDB for analytical marts and LanceDB for vector search over permitted text.

## Consequences

- Excellent local analytical performance.
- Good fit for public reproducible datasets.
- Requires clear boundaries between tabular truth and semantic retrieval suggestions.
