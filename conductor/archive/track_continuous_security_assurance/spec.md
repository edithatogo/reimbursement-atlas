# Continuous security assurance and branch enforcement

## Scope

Continuously inspect repository security settings, scan complete history for
secrets, enforce required security/harness checks through branch-protection
contracts, and preserve explicit account-level limitations.

## Acceptance criteria

- Scheduled read-only monitoring emits redacted security-settings state and
  distinguishes `blocked_account` from `blocked_permissions`.
- Secret-history, action pinning, workflow-policy and branch-protection
  contracts pass locally.
- Required checks are represented in the branch-protection contract without
  inferring hosted completion from local tests.
- Account-level GitHub settings remain explicit blockers when unavailable or
  disabled; compensating controls are documented and active.
