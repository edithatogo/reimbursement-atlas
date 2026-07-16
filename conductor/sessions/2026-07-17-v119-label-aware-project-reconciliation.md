# Conductor session: label-aware Project reconciliation

## Scope

Hardened the idempotent GitHub issue and Project synchronizer so generated backlog drafts can be
reconciled even when the generated label taxonomy is ahead of the repository's current labels.

## Changes

- Added live label discovery through the GitHub CLI.
- Issue creation now passes only labels that exist remotely and reports skipped labels explicitly.
- Added typed label-response parsing and focused regression coverage.
- Updated operator documentation and Conductor acceptance criteria.

## Safety boundary

The synchronizer remains read-only by default. With explicit `--apply`, it may create missing
issues and add Project items, but it does not create or mutate labels, edit existing issues,
close/delete issues, merge, force-push or expose credentials.

## Validation

- `pixi run format`
- `pixi run lint`
- `pixi run typecheck`
- `pixi run python -m pytest tests/unit/test_v18_contract_project_handoff.py -q`
- `pixi run github-project-sync` reports 26 exact missing issue drafts before apply.
