# Session: v7 dashboard, Node validation and mutation wiring

## Summary

This pass answered the open question about installing the missing tools. The local environment now uses `uv sync --all-extras` for the Python toolchain and `npm ci` for the dashboard. The Astro/Cosmograph dashboard builds successfully and has navigable source, analysis, crosswalk, ontology and readiness pages.

## Implemented

- Generated and committed `uv.lock`.
- Generated and committed `apps/dashboard/package-lock.json`.
- Switched dashboard CI from `npm install` to `npm ci`.
- Added npm audit to security workflow.
- Fixed Papaparse TypeScript typing.
- Added a Cosmograph/gl-bench ESM alias in Astro config.
- Added dashboard layout, data-table component and dashboard-safe build-time CSV reader.
- Added routes for `/sources/`, `/analyses/`, `/crosswalks/`, `/ontologies/` and `/readiness/`.
- Added dashboard smoke tests for lockfile and required public data assets.
- Added `pythonpath = ["src"]` for pytest so mutmut can import mutated source code correctly.
- Added mutation-testing and dashboard-validation docs.

## Validation

Validated locally:

- `uv sync --all-extras`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run basedpyright`
- `uv run pytest --cov=src/reimburse_atlas --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -q`
- `uv run bandit -q -c pyproject.toml -r src scripts`
- `uv build`
- `npm ci`
- `npm audit --omit=dev --audit-level=moderate`
- `npm run build`

`pip-audit` remains blocked in this runtime by DNS resolution to pypi.org. Full `mutmut run` is wired correctly but is long-running: it generated 3,673 mutants across 45 files and started evaluating them before the interactive timeout.

## Next recommended step

Create a narrower mutation-smoke profile and then manually validate one reviewed MBS or CMS source file through the reviewed-source bundle workflow without committing raw source data.
