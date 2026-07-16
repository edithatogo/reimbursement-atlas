# Verify reproducible Python release artefacts in CI

Epic: `SEC-020` — Continuous security assurance and branch enforcement

Labels: type:supply-chain, type:release, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: CI builds twice with a fixed `SOURCE_DATE_EPOCH` and compares artifact names and bytes.
- [x] Licence and data-governance implications are checked through the release manifest and publication policy.
- [x] Tests or validation evidence are defined by the required `reproducible-build` check and uploaded checksum evidence.
- [x] Documentation or Conductor context is updated in `docs/RELEASE_VERIFICATION.md`.
