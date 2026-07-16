# Record redacted PBS API multi-endpoint acquisition evidence

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:data-quality, type:provenance, type:parser, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: schedules, paginated items and fees are represented by redacted counts, columns, checksums and review status.
- [x] Licence and data-governance implications are checked: raw API responses remain ignored and the subscription key is never recorded.
- [x] Tests or validation evidence are defined by PBS acquisition evidence tests and source-contract validation.
- [x] Documentation or Conductor context is updated; derived publication remains pending source and licence review.
