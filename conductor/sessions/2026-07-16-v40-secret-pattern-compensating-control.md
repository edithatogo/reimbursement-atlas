# Session v40: secret-pattern compensating control

## Scope

Clarify the security boundary for GitHub issue #191 without claiming an unavailable account feature.

## Evidence

- `.github/workflows/security-assurance.yml` runs the SHA-pinned `gitleaks/gitleaks-action` with full
  history on pull requests, pushes to `main` and a weekly schedule.
- The `secret-history` protected check passes in the current GitHub matrix.
- GitHub provider secret scanning and push protection remain enabled.
- GitHub non-provider pattern scanning and validity checks remain disabled in the live account API.

## Decision

Treat Gitleaks as repository-owned compensating coverage. Keep issue #191 open for the distinct
GitHub Advanced Security account setting; do not represent Gitleaks as equivalent functionality.
