# ADR 0011: Reviewed source bundles before broader live ingestion

## Status

Accepted.

## Context

The project needs to move beyond synthetic fixtures without accidentally committing raw source files, proprietary descriptors or restricted ontology content.

## Decision

Add a reviewed-source-bundle workflow that snapshots a manually downloaded local file, parses it, and writes only checksum metadata, derived rows and validation/publication-review reports.

## Consequences

- Live validation can start source-by-source without network automation.
- Raw files remain in ignored local paths.
- Publication review is explicit rather than implied by successful parsing.
- Future CI can inspect bundle manifests without needing raw files.
