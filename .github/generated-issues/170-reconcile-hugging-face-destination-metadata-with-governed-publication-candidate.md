# Reconcile Hugging Face destination metadata with governed publication candidate

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:repo-automation, risk:licence, phase:release-gate, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: read-only verification identifies the configured dataset and Space and records current destination metadata.
- [x] Licence and data-governance implications are checked: remote mutation remains blocked until the governed candidate gates pass.
- [x] Tests or validation evidence are defined: the Hugging Face candidate workflow builds and validates both bundles with publication flags disabled.
- [x] Documentation or Conductor context is updated with the current destination drift.
- [ ] Dataset card and Space metadata match the governed candidate, including the Apache-2.0 code and source-specific data-licence boundary.
- [ ] Licence, research, evidence and policy-claim gates are approved before a write-enabled reconciliation run.
