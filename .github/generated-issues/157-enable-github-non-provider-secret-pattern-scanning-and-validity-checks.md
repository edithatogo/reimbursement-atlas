# Enable GitHub non-provider secret-pattern scanning and validity checks

Epic: `SEC-020` — Continuous security assurance and branch enforcement

Labels: type:security, type:repo-automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] A scheduled read-only monitor records the four repository security settings without tokens or request headers.
- [x] The monitor records disabled account/plan-bound advanced controls as externally unavailable, never as enabled.
- [x] The monitor reports blocked_permissions when an authenticated API response omits security analysis settings, rather than inferring an account state.
- [x] Core scanning, push protection, Gitleaks, CodeQL, zizmor and dependency-review compensating controls remain documented.
- [x] Live owner-visible readback confirms secret scanning and push protection are enabled; unavailable optional controls are non-required external observations.
