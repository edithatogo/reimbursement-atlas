# Session: v199 GitHub security-settings token boundary

## Scope

Recheck the live GitHub security controls and improve the scheduled monitor's ability to read
repository security-analysis settings without granting mutation rights.

## Evidence

- Authenticated repository API PATCH returned HTTP 200 but preserved
  `secret_scanning_non_provider_patterns=disabled` and
  `secret_scanning_validity_checks=disabled`.
- The local administrator readback reports core scanning and push protection enabled, with both
  advanced controls disabled. No secret values were accessed or recorded.
- Monitor run `29596092769` completed successfully, but its default `GITHUB_TOKEN` could not see
  the security-analysis object and correctly reported `blocked_permissions`.

## Implementation

- The monitor now accepts optional repository secret `GH_SECURITY_SETTINGS_TOKEN` and falls back
  to `GITHUB_TOKEN`.
- The documented token contract is fine-grained, repository-scoped, read-only
  `administration:read`; the workflow remains read-only and never performs a PATCH.
- Issue #191 remains blocked until the live API reports both advanced controls as `enabled`.

## Boundary

Repository-owned compensating controls remain active. Account/plan-bound GitHub settings and the
optional secret configuration are external administration work and are not claimed complete.
