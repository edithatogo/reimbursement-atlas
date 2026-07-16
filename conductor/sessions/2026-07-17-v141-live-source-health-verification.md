# Session v141: live source-health verification

Date: 2026-07-17
Track: `track_live_source_ingestion`
Related issues: #25, #383

## Objective

Replace stale acquisition assumptions with a current network-enabled source-health run while
preserving credential, raw-data and licence boundaries.

## Evidence

- Workflow run: https://github.com/edithatogo/reimbursement-atlas/actions/runs/29538465869
- Conclusion: `success`
- Source validation, source contracts, source drift and release-readiness enforcement passed.
- Acquisition status: `incomplete`, exactly one target incomplete.
- Generated issue: https://github.com/edithatogo/reimbursement-atlas/issues/383

## Current boundary

PBS remains incomplete because `PBS_API_SUBSCRIPTION_KEY` is not present in the approved GitHub
Actions secret store. The workflow did not log or commit a key, raw source payload, or licence-gated
descriptor. MBS and other source states remain governed by their existing clinical/licence review
criteria.

## Next action

Provide the current PBS key through the approved secret store, rerun the hardened acquisition, then
run source validation, source contracts, data quality, evidence readiness and release-readiness before
any reviewed-source promotion.
