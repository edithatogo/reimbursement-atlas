# Gate OSF publication on protocol-status readiness table

Epic: `OSF-002` — Protocol completeness and OSF release gates

Labels: type:research, type:osf, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: OSF mutation commands fail closed when protocol status is not ready.
- [x] Licence and data-governance implications are checked: blocked rows are not published or silently relabelled.
- [x] Tests or validation evidence are defined: protocol-status and OSF sync tests cover blocked registration and publication actions.
- [x] Documentation or Conductor context is updated in `docs/OSF_RECONCILIATION.md`; registration still requires accountable review.
