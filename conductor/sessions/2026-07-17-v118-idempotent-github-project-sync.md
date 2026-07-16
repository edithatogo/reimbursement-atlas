# Conductor session: idempotent GitHub Project synchronisation

## Scope

Implemented a repository-local synchroniser that reconciles generated issue drafts with the
live repository and Conductor Project #18 without making implicit remote changes.

## Changes

- Added `scripts/sync_github_project.py` and the `pixi run github-project-sync` task.
- Made the default mode read-only and exact-title based; writes require explicit `--apply` and
  optional repeated `--title` filters.
- Added response-shape handling for GitHub CLI Project JSON and duplicate-aware tests.
- Added backlog, generated issue and Project-row linkage plus operator documentation.

## Safety boundary

The synchroniser can create missing issues and add missing Project items only when explicitly
requested. It never edits, closes, deletes, merges, force-pushes or exposes credentials. Similar
but non-identical issue titles remain a human reconciliation task.

## External verification

- Grouped licence review issue #326 exists and is present in Project #18.
- A filtered dry run reports `present` for issue #326 and does not write remotely.

## Validation

- `pixi run format`
- `pixi run lint`
- `pixi run typecheck`
- `pixi run python -m pytest tests/unit/test_v18_contract_project_handoff.py -q`
- `pixi run github-project-sync --title "Add grouped licence review packet for accountable handoff"`
