# Session v80: Hugging Face dataset-card contract

Date: 2026-07-16
Track: `track_publication_hf_spaces`
Roadmap linkage: CI/CD hardening recommendation 5

## Implemented

- Added required dataset-card metadata and licensing disclosure markers to
  `scripts/check_huggingface_bundle.py`.
- Added focused pass/fail tests for the governed card contract.
- Added the validator to the pull-request data-smoke workflow.
- Updated the CI/CD hardening documentation, Conductor backlog, current focus and decision log.

## Boundary

The contract verifies publication metadata hygiene only. It does not approve MBS, PBS, CMS,
ontology or other source licences, and it does not publish to Hugging Face.

## Validation

Run `pixi run hf-bundle` and the focused Hugging Face unit tests. The full protected workflow
must pass before merge.
