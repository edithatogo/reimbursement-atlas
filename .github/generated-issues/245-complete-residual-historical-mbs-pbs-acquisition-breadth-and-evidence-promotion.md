# Complete residual historical MBS/PBS acquisition breadth and evidence promotion

Epic: `TRACK_PBS_RAW_ARCHIVE_20260831` — PBS source archive staging and early-schema evidence

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
- [ ] Recover the December 1987 RPBS PDF: canonical URL returned HTTP 404 and the variant returned HTTP 403; the NLA holdings lead remains uninspected, with no publisher/library contact claimed.
- [ ] Recover December 2006-March 2007 XML payloads and release-specific schema/DTD/XSL, amendment and version metadata; do not infer field parity.
- [x] Accept and apply the owner's 2026-08-31 raw PBS redistribution attestation in data/licence_review/pbs_raw_permission.json; no per-file approval required.
- [x] Close permission implementation through PR #801 (`02116d73`), independently of the active source archive track `track_pbs_raw_archive_20260831`.
- [x] Implement offline staging and exact-inventory readback with duplicate-key rejection, original filenames, permission-record SHA and CDX-bound replay identity.
- [x] Retain initial and superseding full-corpus dry runs: 1,707 of 1,709 receipts verify after the identity fix; missing 1987 acquisition and the excluded format notice remain explicit. At those dry runs, no actual staging or upload occurred.
- [x] Subsequently verify the orchestrator's local stage: 1,707 payloads, 9,216,771,435 bytes, zero failures; report and manifest SHA-256 `569d18a843791e666be9e878e52859355d48f8cce76cabf1f7b97034c7ae12ff`. Remote upload/readback have not occurred; publication remains `not_asserted`.
- [x] Integrate two early schema distributions and three verified HTML indexes as metadata only; no missing monthly release, schema compilation or RPBS PDF recovery.
- [x] Prepare conditional raw/pbs dataset-card documentation while retaining all eight derived configs and the existing derived workflow's raw rejection.
- [x] Complete isolated source regeneration and the 27 native quality gates; refresh action inventory and downstream projections after PR #800.
- [x] Complete independent archive-contract and concurrent-push preservation review (Erdos PASS reported).
- [ ] Complete protected source-PR delivery; selected subsets must retain full omission evidence.
- [ ] Transfer raw PBS files to governed external storage with manifest and checksum readback; permission alone is not evidence of publication.
- [x] Promote only independently licence-reviewed permitted metadata or derived fields; GitHub Actions run 33237003418 published the governed Hugging Face configurations without raw payloads or the legacy seed tree.
