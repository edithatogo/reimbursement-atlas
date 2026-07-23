# Schedule read-only Hugging Face destination metadata drift monitoring

Epic: `PUB-001` — Publication and dataset release readiness

Labels: type:publication, type:repo-automation, risk:licence, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The scheduled/manual workflow uses read-only public API requests and contents-read permissions.
- [x] The report records only repository identity, expected card fields, drift reasons and mutation_performed=false.
- [x] The workflow has no HF token, clone, push, or write-enabled publication step.
- [x] Drift remains linked to issue #320 and does not imply publication approval.
- [x] The workflow synchronizes issue #320 with the redacted read-only report using only GitHub issue permission.
- [x] The report includes target-specific remediation steps that remain gated and non-mutating.
