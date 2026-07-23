# Add idempotent dry-run-by-default GitHub Project synchronizer

Epic: `DX-001` — Developer experience and release hardening

Labels: type:automation, type:repo-automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Generated issue drafts are compared with all remote issues by exact title before any write.
- [x] The default command is read-only and reports missing issue and Project-item actions.
- [x] Writes require explicit --apply and optional exact-title filters; no destructive GitHub operation is exposed.
- [x] Unavailable GitHub labels are skipped and reported without aborting issue or Project-item reconciliation.
- [x] Documentation and focused tests define the credential and duplicate-avoidance boundary.
