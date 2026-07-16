# v105 post-merge recommendation audit

## Objective

Continue the recommendation queue after the toolchain evidence redaction merged, while preserving
the distinction between repository-local completion and external publication or human-review gates.

## Evidence

- PR #311 merged to `main` as `bbb83e8770b8b73b3df8f3b817565eb7b1944328`.
- Required CI checks passed, including deterministic regeneration, generated-artifact parity,
  layered tests, dashboard/browser validation, Python 3.14, CodeQL, dependency review, zizmor,
  secret-history, readiness and reproducible-build checks.
- Local post-merge checks passed: public-data policy, seed synchronization, CLI validation, the
  focused toolchain unit suite (7 tests), Ruff and basedpyright.
- The committed toolchain evidence now uses stable `PATH:<executable>` identifiers rather than
  workstation-specific executable paths.
- The repository is clean on `main`.

## Decisions

1. Keep the July 2026 MBS derived bundle and PBS extract in review-gated status. The raw payloads
   remain ignored and no source licence or human research decision is inferred from parser success.
2. Keep OSF, Hugging Face and Zenodo workflows fail-closed until protocol, licence, evidence and
   publication approvals are recorded.
3. Keep GitHub non-provider secret-pattern scanning and validity checks as an explicit account-level
   blocker. Provider scanning, push protection, Dependabot and repository-owned Gitleaks history
   scanning remain the active compensating controls.
4. Export the merged repository as a Git bundle and tracked-files-only archive with SHA-256
   checksums for handoff.

## Remaining next actions

- Human-review the MBS bundle and PBS extract, then promote only approved derived fields.
- Complete CMS CLFS, ASP and PFS parser validation under their licence constraints.
- Adjudicate mapping calibration controls and approve the intended evidence threshold.
- Obtain explicit publication approval before any OSF, Hugging Face or Zenodo mutation.
- Recheck GitHub account-plan availability for the two advanced secret controls.
