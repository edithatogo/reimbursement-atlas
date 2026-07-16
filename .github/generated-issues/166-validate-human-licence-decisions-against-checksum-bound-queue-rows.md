# Validate human licence decisions against checksum-bound queue rows

Epic: `EVID-017` — Evidence readiness, source drift and data dictionary gates

Labels: type:publication, type:review, risk:licence, phase:release-gate, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: validate queue integrity and optional human decision rows; do not infer approval.
- [x] Licence and data-governance implications are checked: decisions require source terms, attribution, permission, restrictions and evidence.
- [x] Tests or validation evidence are defined: `pixi run licence-review-validate` plus stale-checksum and incomplete-decision tests.
- [x] Documentation or Conductor context is updated; CI runs the validator.
- [ ] An accountable human has reviewed each candidate artefact before any approval record is added.
