# ADR 0017: Exact source-file records before live ingestion

Date: 2026-07-04

## Status

Accepted.

## Context

A source registry row such as CMS CLFS or Australian MBS is not granular enough for reproducible ingestion. The project needs exact file names, endpoint pages, licence gates, expected formats and acquisition modes before a parser can be promoted.

## Decision

Add `SourceFileRecord` and `data/seed/source_files.*` as a metadata-only acquisition layer. The records can point to exact public files, landing pages, API documentation, or licence-gated downloads.

## Consequences

- Source-file metadata can be graphed and surfaced in the dashboard.
- Raw files still remain ignored in `data/raw_live/` by default.
- CMS CLFS and other licence-gated resources can be represented without automating click-through or redistributing restricted descriptors.
