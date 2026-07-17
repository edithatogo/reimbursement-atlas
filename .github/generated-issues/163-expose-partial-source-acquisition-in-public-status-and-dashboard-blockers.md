# Expose partial source acquisition in public status and dashboard blockers

Epic: `HANDOFF-018` — Final local continuation and GitHub Project handoff gates

Labels: type:dashboard, type:data-quality, type:handoff, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Public status emits a `source_acquisition` blocker only for operational incomplete or unknown source-health states.
- [x] Review-only source-health status remains visible through licence-review blockers and dashboard source-health evidence.
- [x] Dashboard status and source-health CSV projections regenerate deterministically.
