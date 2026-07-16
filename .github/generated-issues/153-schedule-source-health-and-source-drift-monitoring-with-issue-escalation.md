# Schedule source-health and source-drift monitoring with issue escalation

Epic: `REL-001` — Release readiness and architecture gates

Labels: type:data-quality, type:automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: the scheduled monitor runs acquisition, validation, contract, drift and release-readiness checks without publishing source payloads.
- [x] Licence and data-governance implications are checked: raw downloads remain ephemeral and issue reports contain only derived evidence and secret names.
- [x] Tests or validation evidence are defined: source-health workflow policy and issue-escalation contract tests, plus `pixi run source-health-report`.
- [x] Documentation or Conductor context is updated; failure and incomplete-acquisition issues are opened or updated, and clear acquisition issues are closed.
- [x] Workflow issue mutation is least-privilege and scoped to the source-health job.
