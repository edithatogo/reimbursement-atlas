# Session v140: GitHub issue-body sync retry

Date: 2026-07-17
Track: `track_ci_cd_supply_chain`
Related issue: #176

## Objective

Make the generated GitHub issue-body synchronizer safe for a large, idempotent reconciliation when
GitHub returns transient availability errors.

## Work completed

- Reconciled generated issue bodies against the remote repository with explicit `--apply`.
- The first run updated 67 of 119 detected bodies before a transient HTTP 504 at issue #66.
- Added bounded retries for HTTP 502/503/504 and timeout failures, with exponential backoff.
- Reran the reconciliation and verified 172 remote issues as `present` with no pending body updates.
- Preserved dry-run-by-default behavior and did not change issue state, labels, Project membership or
  publication/research gates.

## Validation

```text
pixi run github-project-sync
present: 172
```

Focused lint, format and unit tests passed before this change. Full `pixi run qa` remains the merge
gate for the PR.

## Remaining boundary

The synchronizer does not approve, close, promote or publish work. Human review, source licensing,
OSF/Hugging Face credentials and evidence-readiness gates remain external blockers.
