# Use one canonical evidence-release readiness model

Epic: `READINESS-CANONICAL-001` — Canonical evidence-release readiness semantics

Labels: type:data-quality, type:governance, status:in-progress

Status: `in_progress`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Medallion and release summaries use the same complete gate result.
- [ ] Partial evidence counts cannot promote Platinum products.
- [ ] Current-run medallion evidence is evaluated without a generated-file cycle.
- [ ] Regression, deterministic-generation and hosted checks pass.
