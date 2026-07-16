# Session v88: GitHub secret-control API recheck

Date: 2026-07-16

## Scope

Retry the two advanced GitHub secret-scanning controls using authenticated REST PATCH requests
with explicit nested JSON payloads, then verify the authoritative repository state.

## Evidence

- PATCH for `secret_scanning_non_provider_patterns` was accepted and returned the repository.
- PATCH for `secret_scanning_validity_checks` was accepted and returned the repository.
- A subsequent repository response still reported both controls as `disabled`.
- Provider secret scanning, push protection and Dependabot remain enabled.
- Full-history Gitleaks remains an independent repository workflow control.

## Boundary

No secret values were read, written or recorded. The controls remain blocked by the GitHub account
or plan capability; the repository does not claim them as enabled.
