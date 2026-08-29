# Complete residual historical MBS/PBS acquisition breadth and evidence promotion

Epic: `TRACK_LIVE_SOURCE_INGESTION` — Evidence-grade live source ingestion

Labels: type:roadmap-function, priority:must, interface:data_pipeline, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria before opening it in GitHub.

## Acceptance criteria

- [x] Historical inventory, backfill/replay contracts and target-level review evidence are implemented.
- [x] 341 of 343 MBS targets are acquired; two confirmed official HTTP 404 targets remain `upstream_unavailable`.
- [x] 1,048 of 1,049 official PBS publication PDFs are signature-validated in ignored storage with SHA-256 receipts.
- [x] All 655 discovered machine-readable PBS packages from 2007 onward are signature-validated with SHA-256 receipts.
- [x] Internet Archive CDX comparison establishes 298 exact PDF digest matches and four checksum-verified historical byte variants.
- [x] Rights states, provenance and non-publication boundaries remain explicit.
- [x] Tests cover historical indexing, deterministic replay, source contracts and raw path exclusion.
- [x] Recover all 110 bounded PBS timeout failures through a low-concurrency retry.
- [ ] Reconcile the remaining December 1987 official HTTP 403 with the publisher.
- [ ] Identify pre-2007 machine-readable sources and version-specific field contracts if broader structured parity is required.
- [ ] Obtain explicit permission before redistributing raw PBS payloads; public download availability does not grant republication rights.
- [ ] Promote only independently licence-reviewed permitted metadata or derived fields.
