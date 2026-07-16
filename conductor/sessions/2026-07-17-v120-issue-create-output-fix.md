# Conductor session: plain-text issue-create response handling

## Scope

Fixed the GitHub CLI response adapter discovered during exact-title Project reconciliation.

## Changes

- `_run_gh` now accepts JSON responses and the plain-text issue URL returned by
  `gh issue create`.
- The apply operation remains idempotent: the first issue created before the failure is detected
  on the next run and will not be duplicated.

## External state

The first apply attempt created one exact issue before stopping at response parsing. No rollback
was performed; the corrected rerun will reconcile that issue and add its missing Project item,
then create and add the remaining exact-title drafts.

## Validation

- `pixi run format`
- `pixi run lint`
- `pixi run typecheck`
- `pixi run python -m pytest tests/unit/test_v18_contract_project_handoff.py -q`
