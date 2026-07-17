# Session v194: bind current-state documentation

Date: 2026-07-18

## Finding

After PR #449 merged as `e639490`, the authoritative handoff and readiness pages still
contained older commit identifiers in their current-state sections. The older monitor records
are valid audit evidence, but the headings were not sufficient to prevent readers from treating
historical snapshots as current.

## Implementation

- Updated current-state references in `docs/FINAL_HANDOFF.md`, `docs/RELEASE_READINESS.md`,
  `docs/OSF_WORKFLOW.md`, `docs/ZENODO_RELEASE_PREPARATION.md` and
  `conductor/context/CURRENT_FOCUS.md`.
- Corrected the current licence-review candidate count from 161 to 163.
- Added a documentation freshness invariant that binds those five files to the checked-out
  full commit SHA.
- Added PR-aware validation: pull-request merge refs require one consistent full SHA across all
  five documents, while local and push-to-main contexts validate against available git parents.
- Configured the Python CI checkout with `fetch-depth: 2` to expose a parent whenever the merge
  ref provides one.
- Retained historical monitor records and explicitly labelled them as historical evidence.

## Verification

- `pixi run docs-freshness` passed.
- `PYTHONPATH=src uv run pytest tests/unit/test_public_product_dashboard.py -q` passed: 6 tests.
- `git diff --check` passed.

No raw source payloads, credentials or external services were mutated.
