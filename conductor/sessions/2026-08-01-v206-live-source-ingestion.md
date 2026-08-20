# Live-source ingestion checkpoint

- Track: `track_live_source_ingestion`
- Backlog: `LIVE-001`
- Date: 2026-08-01
- Branch: `codex/track-live-source-ingestion`

## Completed in this checkpoint

- Ran the hardened HTTPS acquisition plan and recorded 11 redacted attempts.
- Downloaded the July 2026 MBS item-map TXT, descriptor TXT and XML payloads into
  ignored `data/raw_live/au_mbs/` storage.
- Re-ran source-content validation and source-contract validation: 3 pass, 8
  explicit skips, 0 failures, 0 missing and 0 warnings.
- Parsed the real MBS TXT pair into 14,856 derived schedule records.
- Confirmed raw payloads are not copied into the derived bundle and local paths
  are redacted from publication metadata.
- Ran the focused source/parser/policy test set: 24 tests passed.
- Public-data policy validation passed.

## Explicit remaining gates

- The MBS derived bundle remains `public_reuse_review`; publication requires a
  source-specific licence decision before the row set can be released.
- CMS CLFS, ASP and PFS parser validation remains blocked because the available
  targets are licence-gated or contain CPT/HCPCS-restricted material.
- PBS API refresh remains credential-gated; the existing local extract is retained
  and the API path remains available for a later credentialed acquisition.
- The first real-source review is not inferred from parser success. Clinical,
  source-content and licence review evidence remains required.

## Evidence

- `data/derived/source_downloads/download_attempts.jsonl`
- `data/derived/source_validation/summary.json`
- `data/derived/source_contracts/summary.json`
- `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/validation_report.json`
- `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/publication_manifest.json`

The track is not archived because the remaining LIVE-001 acceptance gates are
external or human/licence-bound.
