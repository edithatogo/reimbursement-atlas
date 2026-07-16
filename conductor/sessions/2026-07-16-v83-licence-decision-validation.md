# Session v83: checksum-bound licence decision validation

Date: 2026-07-16
Track: `track_data_quality_evidence`

## Implemented

- Added a typed validator for generated licence-review queue rows and optional human decision
  records.
- Added the `licence-review-validate` Pixi task and CLI-compatible script.
- Added adversarial tests for stale candidate checksums and incomplete decisions.
- Added CI regeneration checks and a documented `data/licence_review/decisions.jsonl` input.
- Added the work item to the Conductor backlog for generated GitHub issue/project synchronisation.

## Boundary

The current decisions file is absent, so all candidate rows remain pending. The validator does
not approve, publish or mutate any source or remote service; it only rejects malformed, stale or
insufficiently evidenced human decision records.

## Validation

- `pixi run format-check`
- `pixi run lint`
- `pixi run typecheck`
- `PYTHONPATH=src pixi run python -m pytest tests/unit/test_licence_review.py -q`
- `pixi run licence-review-validate`
