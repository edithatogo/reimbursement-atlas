# Enable GitHub non-provider secret-pattern scanning and validity checks

Epic: `SEC-020` — Continuous security assurance and branch enforcement

Labels: type:security, type:repo-automation, phase:hardening, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: request and verify the two distinct GitHub security settings.
- [x] Licence and data-governance implications are checked: no secret values are recorded in repository artefacts.
- [x] Tests or validation evidence are defined: full-history Gitleaks CI and live repository-settings API evidence.
- [x] Documentation or Conductor context is updated.
- [ ] GitHub reports `secret_scanning_non_provider_patterns=enabled`.
- [ ] GitHub reports `secret_scanning_validity_checks=enabled`; current account state remains disabled for both.
