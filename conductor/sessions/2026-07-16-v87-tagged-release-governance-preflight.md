# Session v87: tagged-release governance preflight

Date: 2026-07-16

## Scope

Require tagged GitHub releases to pass repository-owned governance checks before creating release
assets, SBOM attestations or a GitHub release.

## Change

Added a least-privilege `preflight` job to `.github/workflows/release.yml`. The existing
write-enabled build job now depends on it and cannot run unless these checks pass:

- `pixi run release-readiness`
- `pixi run public-data-policy`
- `pixi run licence-review-validate`
- `pixi run action-pin-policy`

## Boundary

This protects software release automation only. It does not convert repository release readiness
into research publication, evidence, policy-claim, OSF, Hugging Face or Zenodo approval.
