# Make research package descriptors deterministic and non-self-referential

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:quality, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: Frictionless, RO-Crate and DCAT descriptors describe licence-safe derived artefacts only.
- [x] Licence and data-governance implications are checked: descriptor files are excluded from the candidate manifest and do not change source-data terms.
- [x] Tests or validation evidence are defined: deterministic regeneration and non-self-reference contract tests.
- [x] Documentation or Conductor context is updated in the publication-manifest descriptor-determinism section.
