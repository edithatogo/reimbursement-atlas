# ADR 0027: Harden source download plans before live ingestion

## Status

Accepted.

## Context

The project needs to download public files using `curl`, `wget` or APIs where permitted, while still avoiding raw-data leakage and licence bypass.

## Decision

Source download plans now generate quoted, resumable, metadata-capturing commands and refuse to execute licence-gated or metadata-only records. Download attempts write ignored local sidecar metadata with checksums, bytes and status, but raw files remain outside git.

## Consequences

The repo can move toward real-source ingestion without relying on vague manual instructions. Network failures are recorded as acquisition evidence, and future source-specific validators can use the sidecar metadata.
