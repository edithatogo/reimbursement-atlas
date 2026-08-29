# Historical PBS publication archive

Date: 2026-08-29

## Outcome

- Discovered 1,049 official PBS Schedule publication PDF targets spanning 1951-03-01 through
  2026-07-01, including the 1951-2002 historical page and annual pages from 2003 onward.
- Acquired and signature-validated 938 PDFs (89.4185%; 4,658,177,952 bytes) into ignored local
  storage with tracked SHA-256 receipts.
- Retained 110 bounded timeouts and one official HTTP 403 as explicit failed states.
- Added official-host enforcement, PDF/ZIP magic validation, target discovery, medallion,
  backfill/replay, publication-manifest and dashboard metadata integration.

## Boundaries

- Publication PDFs are not structured API snapshots and do not establish historical API parity.
- No raw PDF, credential, restricted descriptor or local absolute path is tracked.
- Download does not grant redistribution rights; evidence promotion remains independently gated.
- Papers and preprints remain excluded.

## Evidence

- `data/seed/historical_pbs_archive_targets.jsonl`
- `data/derived/historical_sources/pbs_archive_v1/targets_summary.json`
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads_summary.json`
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl`
