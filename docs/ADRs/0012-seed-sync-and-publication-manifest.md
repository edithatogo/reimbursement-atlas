# ADR 0012: Seed sync checks and publication manifests

## Status

Accepted.

## Context

The repo tracks JSONL and CSV mirrors for seed tables. Stale CSV mirrors can mislead the dashboard and downstream release packaging. Public dataset export also needs checksum and row-count evidence.

## Decision

Add:

- JSONL/CSV seed-file synchronisation checks;
- a `sync_seed_csvs.py` task;
- a publication-manifest generator for seed and derived candidate artefacts;
- CI-ready tasks for `seed-sync-check` and `publication-manifest`.

## Consequences

The dashboard, seed lake and future Hugging Face dataset export use auditable generated metadata. Raw/local cache paths remain excluded by policy.
