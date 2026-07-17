# Session v142: PBS credentialed acquisition

Date: 2026-07-17
Track: `track_live_source_ingestion`
Related issues: #25, #383

## Objective

Resolve the PBS runner credential boundary without exposing the public-user subscription key, then
verify the hardened acquisition on GitHub Actions.

## Evidence

- Secret existence: `gh secret list` reports `PBS_API_SUBSCRIPTION_KEY` without revealing its value.
- Workflow run: https://github.com/edithatogo/reimbursement-atlas/actions/runs/29539008697
- Conclusion: `success`
- PBS v3 schedules response: downloaded; provenance records `Subscription-Key: [REDACTED]`.
- Source validation, source contracts, source drift and release-readiness enforcement passed.

## Remaining boundary

The source-health acquisition status remains `incomplete` because six historical MBS/CMS targets are
intentionally `skipped_licence_gate`. This is not a PBS credential failure. No licence-gated payload
was fetched or promoted, and issue #383 remains open until the governed source-review boundary is
resolved.

## Next action

Review the MBS/CMS licence packets and approve only the derived fields permitted for publication.
After review, rerun the source-health workflow and regenerate source validation, contracts, data
quality, evidence readiness and release-readiness outputs.
