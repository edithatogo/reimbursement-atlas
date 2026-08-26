# Expand reviewed coverage with historical MBS and PBS bundles

Epic: `TRACK_LIVE_SOURCE_INGESTION` — Evidence-grade live source ingestion

Labels: type:roadmap-function, priority:must, interface:data_pipeline, status:planned

Status: `planned`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria before opening it in GitHub.

## Acceptance criteria

- [x] Historical inventory, backfill/replay contracts and target-level review evidence are implemented.
- [x] 340 MBS snapshots are acquired in ignored storage with immutable checksums and replay-eligible evidence.
- [x] Rights states, provenance and non-publication boundaries remain explicit.
- [x] Tests cover historical indexing, deterministic replay, source contracts and raw path exclusion.
- [ ] Resolve the three failed historical MBS targets.
- [ ] Acquire and promote rights-reviewed historical PBS payload snapshots; the current historical PBS record is metadata-only.
