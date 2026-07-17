# Session v161: verified handoff package export

## Scope

Automate the final software handoff package required by the Conductor continuation contract.

## Changes

- Added `scripts/export_handoff_bundle.py`.
- Added unit tests for bundle/archive command construction, manifest redaction and prefix safety.
- Added `docs/HANDOFF_PACKAGE_EXPORT.md` with verification commands.
- Added the `HANDOFF-018` Conductor item and generated GitHub Project issue draft.
- Regenerated project, publication, licence, research-package, release-readiness and seed-lake outputs.

## Safety boundary

The exporter writes outside the checkout, uses fixed argument-list git commands without a shell,
verifies the bundle, and records only output basenames. It does not publish to GitHub, OSF,
Hugging Face or Zenodo and cannot convert review-gated evidence into a release claim.

## Validation

- Exporter unit tests pass.
- Ruff format, Ruff lint, basedpyright and public-data policy pass.
- Full deterministic generation and protected CI remain required before merge.
