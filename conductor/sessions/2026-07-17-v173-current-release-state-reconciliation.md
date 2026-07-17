# v173 current release-state reconciliation

## Objective

Remove stale current-commit references from the release-readiness and final-handoff
documentation after the v172 merge.

## Evidence

- Current `main`: `e9b97f8a16a9fc57ad74e95e35d0470294fe0c2a`.
- Current source-health workflow: [29574452434](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29574452434).
- Repository release readiness remains 36/36 gates passing.
- The PBS evidence remains `acquired_unreviewed`; no publication or licence approval is inferred.

## Boundary

Historical workflow identifiers remain in the release-readiness narrative as historical evidence.
The current-state paragraphs now identify the merged v172 commit and source-health run. External
licence, research, OSF, Hugging Face and Zenodo gates remain fail-closed.
