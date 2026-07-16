# Schedule read-only Hugging Face destination metadata drift monitoring

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:repo-automation, risk:licence, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is implemented: the scheduled/manual workflow checks public dataset and Space metadata without credentials or mutation.
- [x] Licence and data-governance implications are checked: the report preserves the source-specific data-licence boundary and remote publication remains gated.
- [x] Tests or validation evidence are defined by the destination contract unit test, action-pin policy and the workflow artifact.
- [x] Documentation or Conductor context is updated; drift remains linked to issue #320.
