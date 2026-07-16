# Add idempotent dry-run-by-default GitHub Project synchronizer

Epic: `DX-001` — Developer experience and release hardening

Labels: type:automation, type:repo-automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is implemented: generated drafts are compared with remote issues and Project items by exact title/number.
- [x] The default command is read-only; writes require explicit `--apply` and optional exact-title filters.
- [x] No destructive issue, merge, branch or credential operation is exposed.
- [x] Documentation and focused tests define the duplicate-avoidance boundary.
