# CI/CD and supply-chain hardening

## Scope

Make repository automation auditable and fail closed through pinned GitHub
Actions, least-privilege workflow permissions, workflow-policy validation,
SBOMs, provenance/attestation hooks, CodeQL, dependency review, OpenSSF
Scorecard, zizmor, secret-history scanning and reproducible-build checks.

## Acceptance criteria

- Workflow references are SHA-pinned and policy output contains no unresolved
  repository-owned failures.
- SBOM and provenance generators produce deterministic, dashboard-safe outputs.
- Security workflows use explicit permissions and preserve read-only checkout
  credentials where mutation is not required.
- Local unit and contract tests cover branch protection, workflow policy,
  attestations, SBOMs and deterministic regeneration.
- Hosted checks and account-level security settings remain separately reported;
  local evidence never claims hosted success.
