# Conductor session: checksum-bound licence review queue

Date: 2026-07-16

## Finding

The repository already generated a conservative publication manifest, but it did not
provide an artifact-level work queue for accountable licence review. Source-level notes
alone made it harder to review candidate outputs against the exact bytes intended for
publication.

## Implementation

- Added `src/reimburse_atlas/licence_review.py` and
  `scripts/make_licence_review_queue.py`.
- Generated JSONL, CSV, summary and operator documentation under
  `data/derived/licence_review/`.
- Bound each of 155 candidates to its SHA-256 checksum and publication metadata.
- Kept all 155 rows `pending`; no generated record can mutate an approval.
- Added the queue to the data dictionary, local quality gates, release readiness,
  Conductor backlog and generated GitHub Project/issue artefacts.
- Added unit coverage and architecture-layer registration.

## Verification

- Local quality: 27/27 passed.
- Release readiness: 36/36 repository gates passed.
- Licence queue: 155 pending, 0 approved, mutation disabled.
- Research publication, evidence release and policy claims remain fail-closed.

## Boundary

Human licence/domain review, protocol approval, public-data release approval and
publication-provider actions remain external gates. This session does not claim those
decisions were made.
