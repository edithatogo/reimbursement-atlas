# Session v192: historical source review packet

Date: 2026-07-18

## Scope

Implemented the repository-owned review handoff for the metadata-only historical
MBS archive inventory. The packet covers the 343 targets discovered across 32
official archive pages without acquiring or embedding any historical payload.

## Changes

- Extended `scripts/make_historical_source_index.py` to generate
  `historical_mbs_review_queue.csv` and `.jsonl`.
- Added explicit `review_status`, `reviewer`, `reviewed_at`, `decision_evidence`
  and `permitted_derived_fields` columns. New rows are always
  `pending_human_review`.
- Exposed the packet in the dashboard readiness view, publication manifest and
  data dictionary while retaining the `public_reuse_review` licence gate.
- Added a focused regression test proving that an empty review record cannot be
  mistaken for approval.
- Updated the live-source track and generated issue #112 acceptance text.

## Validation

- Historical source tests passed: 5 tests.
- Deterministic generators completed, including seed lake, data dictionary,
  publication package, dashboard seed, release readiness and final handoff.
- Repository release readiness remained 36/36 passing with zero required
  blockers.

## Boundary

The packet does not grant permission to download, parse, redistribute or publish
any historical source. Human source-specific licence review, acquisition into
ignored local storage, checksum capture, parser validation and reviewed-derived
bundle promotion remain open work under issue #112.
