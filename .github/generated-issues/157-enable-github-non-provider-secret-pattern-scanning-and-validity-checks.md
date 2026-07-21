# Enable GitHub non-provider secret-pattern scanning and validity checks

Epic: `SEC-020` — Continuous security assurance and branch enforcement

Labels: type:security, type:repo-automation, phase:hardening, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] A scheduled read-only monitor records the four repository security settings without tokens or request headers.
- [ ] The monitor keeps issue #191 synchronized and reports disabled advanced controls as blocked_account, never as pass.
- [ ] The monitor reports blocked_permissions when an authenticated API response omits security analysis settings, rather than inferring an account state.
- [ ] Core scanning, push protection, Gitleaks, CodeQL, zizmor and dependency-review compensating controls remain documented.
