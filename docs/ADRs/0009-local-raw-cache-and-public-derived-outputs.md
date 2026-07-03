# ADR 0009: Local raw cache and public derived outputs

Date: 2026-07-03

## Status

Accepted.

## Context

Public reimbursement sources are often accessible, but redistribution rights and descriptor licensing vary. CMS PFS and CLFS files can involve CPT governance; PBS public prices do not necessarily equal effective net prices; ontology packages can be restricted.

## Decision

Live source files will be downloaded into ignored local cache paths first. The repo will commit source metadata, checksums, parser contracts and derived records only after licence review.

## Consequences

- `data/raw_live/`, `data/raw/`, `data/local/`, `data/cache/` and related paths stay ignored.
- `scripts/check_public_data_policy.py` fails CI if raw/local cache files become tracked.
- `SourceSnapshotRecord` is the gate between a local raw file and a public derived output.
- Dashboard and Hugging Face dataset exports should use derived records, not raw files, unless a source is explicitly approved for public raw caching.
