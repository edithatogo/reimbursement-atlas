# Session v92: branch-protection drift validator

## Objective

Prevent recurrence of the stale required `zizmor` app binding while retaining strict branch
protection and avoiding another required-check deadlock.

## Implementation

- Added `scripts/check_branch_protection.py` with captured-JSON and authenticated live modes.
- Added Pixi task `branch-protection-live`.
- Added unit tests for valid, missing-context and wrong-app contracts.
- Documented administrator usage in `docs/GITHUB_AUTOMATION.md`.
- Added the completed Conductor backlog item and generated issue/project artefacts.
- Created and closed live issue [#279](https://github.com/edithatogo/reimbursement-atlas/issues/279)
  after PR #278 merged; added the completed item to Project #18 as `Done`.

## Evidence

- Fresh GitHub REST response for `main` validated with status `pass` and zero errors.
- BasedPyright: 0 errors, 0 warnings, 0 notes.
- Unit suite: 254 passed.

## Boundary

The validator is read-only. It does not change branch protection, issue status, secrets,
publication settings or source-data licences.
