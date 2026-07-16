# Pin and contract-test the stable OSF CLI command surface

Epic: `OSF-002` — Protocol completeness and OSF release gates

Labels: type:osf, type:automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: the unauthenticated contract checks the pinned version and required help markers without mutating OSF.
- [x] Licence and data-governance implications are checked; credentials are never read by the contract probe.
- [x] Tests or validation evidence are defined in `tests/unit/test_osf_cli_contract.py` and the `osf-cli-contract` Pixi task.
- [x] Documentation or Conductor context is updated; live OSF publication remains gated.
