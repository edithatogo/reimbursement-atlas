# Generate artifact-level licence review queue bound to publication checksums

Epic: `EVID-017` — Evidence readiness, source drift and data dictionary gates

Labels: type:publication, type:review, risk:licence, phase:release-gate, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: every publication candidate is represented by a generated queue row.
- [x] Licence and data-governance implications are checked: rows are checksum-bound and fail closed.
- [x] Tests or validation evidence are defined: deterministic queue generation and licence-review validation.
- [x] Documentation or Conductor context is updated in the queue README and release documentation.
- [ ] Human decisions are recorded for every candidate before publication.
