# Scan complete Git history for committed secrets

Epic: `SEC-020` — Continuous security assurance and branch enforcement

Labels: type:security, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: the protected security workflow checks full Git history with `fetch-depth: 0`.
- [x] Licence and data-governance implications are checked; reports do not publish secret values.
- [x] Tests or validation evidence are defined by the required `secret-history` Gitleaks check.
- [x] Documentation or Conductor context is updated in the security assurance workflow.
