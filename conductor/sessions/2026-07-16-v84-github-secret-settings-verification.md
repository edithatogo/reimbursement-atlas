# Session v84: GitHub secret-setting verification

Date: 2026-07-16
Track: `track_continuous_security_assurance`
Issue: [#191](https://github.com/edithatogo/reimbursement-atlas/issues/191)

## Verification

Authenticated GitHub API requests were made for:

- `secret_scanning_non_provider_patterns=status:enabled`
- `secret_scanning_validity_checks=status:enabled`

Both requests returned successfully but the repository settings API continued to report
`disabled` for both controls. Provider secret scanning, push protection and Dependabot remain
enabled, and the repository-owned full-history Gitleaks workflow remains the compensating control.

## Boundary

This is an account/plan capability blocker, not a missing repository workflow. No secret values,
tokens or API responses containing credentials were recorded. The issue remains open until the
live GitHub settings report both controls as enabled.
