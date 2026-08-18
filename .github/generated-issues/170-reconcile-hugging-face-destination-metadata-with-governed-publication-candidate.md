# Reconcile Hugging Face destination metadata with governed publication candidate

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:repo-automation, risk:licence, phase:release-gate, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Read-only verification records the configured dataset and Space identities and current card metadata.
- [x] Candidate dataset and static Space bundles pass local publication and public-data policy gates.
- [x] Remote mutation is permitted only after licence, research, evidence and policy-claim gates pass.
- [x] The published dataset card declares source-specific licences and the Space declares Apache-2.0 code plus underlying-data restrictions.
