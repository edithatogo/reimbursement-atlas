# Run pip-audit strict in network-enabled CI before public release

Epic: `REL-001` — Release readiness and architecture gates

Labels: type:security, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: CI runs `pip-audit --strict` using the pinned Pixi task.
- [x] Licence and data-governance implications are checked: advisory results do not alter source-data publication terms.
- [x] Tests or validation evidence are defined: the protected `python-security` job and external-quality-gates artefact provide network-enabled evidence.
- [x] Documentation or Conductor context is updated; local advisory lookup remains environment-dependent outside CI.
