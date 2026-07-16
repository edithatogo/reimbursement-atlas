# Add Hugging Face dataset-card contract checks before public release

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:quality, risk:licence, phase:hardening

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: validate versioned dataset-card metadata before any HF publication mutation.
- [x] Licence and data-governance implications are checked: the card distinguishes Apache-2.0 code from source-specific data terms.
- [x] Tests or validation evidence are defined: `pixi run hf-bundle` and focused unit tests.
- [x] Documentation or Conductor context is updated; the pull-request data-smoke workflow runs the contract.
- [ ] Accountable human source-licence approval and HF publication authorization are complete.
