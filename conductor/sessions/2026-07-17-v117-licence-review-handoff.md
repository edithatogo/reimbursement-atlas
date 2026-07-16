# Conductor session: grouped licence review handoff

## Scope

Implemented the next repository-local improvement for the public-product and citation dashboard
track: a deterministic batch summary and reviewer packet for the checksum-bound licence queue.

## Changes

- Added `data/derived/licence_review/licence_review_batches.csv`, grouped by licence gate and
  publication scope with counts, byte totals and raw-payload counts.
- Added `data/derived/licence_review/reviewer_packet.md` with the required human decision fields
  and fail-closed review sequence.
- Added the grouped batch table to the readiness dashboard and regenerated dashboard assets.
- Added Conductor backlog, generated issue and Project-row linkage.

## Boundary

All 159 candidate artefacts remain pending human licence review. The new outputs do not grant
approval, alter the publication manifest, or enable OSF, Hugging Face or other remote mutation.

## Validation

- `pixi run python -m pytest tests/unit/test_licence_review.py -q`
- `pixi run lint`
- `pixi run typecheck`
- `pixi run licence-review-validate`
