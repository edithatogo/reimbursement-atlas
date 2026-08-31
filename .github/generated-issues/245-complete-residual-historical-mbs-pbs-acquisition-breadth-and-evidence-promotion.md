# Complete residual historical MBS/PBS acquisition breadth and evidence promotion

Epic: `TRACK_LIVE_SOURCE_INGESTION` — Evidence-grade live source ingestion

Labels: type:roadmap-function, priority:must, interface:data_pipeline, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria before opening it in GitHub.

## Acceptance criteria

- [x] Historical inventory, backfill/replay contracts and target-level review evidence are implemented.
- [x] Reconcile historical MBS locator failures against checksum-bound reviewed TXT snapshots in `data/derived/historical_sources/mbs_identity_reconciliation.json`; preserve HTTP failure receipts and do not assert current raw-cache availability.
- [x] 1,048 of 1,049 official PBS publication PDFs are signature-validated in ignored storage with SHA-256 receipts.
- [x] All 655 discovered machine-readable PBS packages from 2007 onward are signature-validated with SHA-256 receipts.
- [x] All eight Services Australia PBS Item Report resources are signature-validated with path-free SHA-256 receipts under CC BY 3.0 AU; the 1992-2016 YTD aggregate utilisation lane is kept distinct from Schedule and pricing data.
- [x] Internet Archive CDX comparison establishes 690 exact PDF digest matches and five checksum-verified historical byte variants after transport-neutral matching.
- [x] Rights states, provenance and non-publication boundaries remain explicit.
- [x] Tests cover historical indexing, deterministic replay, source contracts and raw path exclusion.
- [x] Recover all 110 bounded PBS timeout failures through a low-concurrency retry.
- [ ] Reconcile the remaining December 1987 official HTTP 403 with the publisher.
- [ ] Recover December 2006-March 2007 XML payloads and release-specific schema/DTD/XSL, amendment and version metadata; do not infer field parity.
- [x] Accept and apply the owner's 2026-08-31 raw PBS redistribution attestation in data/licence_review/pbs_raw_permission.json; no per-file approval required.
- [ ] Transfer raw PBS files to governed external storage with manifest and checksum readback; permission alone is not evidence of publication.
- [x] Promote only independently licence-reviewed permitted metadata or derived fields; GitHub Actions run 33237003418 published the governed Hugging Face configurations without raw payloads or the legacy seed tree.
