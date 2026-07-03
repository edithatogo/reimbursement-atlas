# ADR 0008: Source snapshots before live ingestion

Date: 2026-07-03

## Status

Accepted.

## Context

The atlas will eventually ingest live public schedules, but even public files can
carry redistribution constraints, version ambiguity, CPT/UMLS/ontology issues or
confidential-price caveats. The project needs a provenance gate between source
acquisition and parser claims.

## Decision

Every committed fixture or reviewed live source file must be represented by a
`SourceSnapshotRecord` before parser outputs are treated as reproducible. The
record captures:

- source and source-version identifiers;
- source URL;
- local path where applicable;
- retrieval timestamp;
- checksum and byte size;
- content type;
- licence gate; and
- cache/publication scope.

Synthetic fixtures may be committed and marked as `public_derived_only` or
fixture-safe. Live raw files should default to local-only until licence review is
complete.

## Consequences

- Parser tests can verify deterministic fixture hashes.
- Future live-source validation has a clear audit trail.
- Hugging Face dataset publishing can filter by cache/publication scope.
- Dashboard/API/MCP surfaces can expose provenance without exposing restricted
  raw files.
