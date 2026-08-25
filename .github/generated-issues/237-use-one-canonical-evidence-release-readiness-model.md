# Use one canonical evidence-release readiness model

Epic: `READINESS-CANONICAL-001` — Canonical evidence-release readiness semantics

Labels: type:data-quality, type:governance, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Medallion and release summaries use the same complete gate result.
- [x] Partial evidence counts cannot promote Platinum products.
- [x] Current-run medallion evidence is evaluated without a generated-file cycle.
- [x] Regression, deterministic-generation and hosted checks pass.
