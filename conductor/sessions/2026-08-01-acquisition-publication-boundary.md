# Acquisition and publication boundary

## Scope

This session implemented the approved blocker-closure recommendations without publishing
restricted source data or submitting papers/preprints.

## Acquisition result

The hardened curl plan recorded 11 attempts in
`data/derived/source_downloads/download_attempts.jsonl` and `.csv`:

- Three MBS XML/TXT payloads were downloaded to ignored `data/raw_live/` storage.
- PBS API documentation was classified `local_cache_available`.
- Historical MBS, PBS download, CMS CLFS, CMS ASP and CMS PFS targets were
  `skipped_licence_gate`.
- The historical inventory remains 343 metadata-only targets across 32 archive pages;
  every target remains `pending_human_review`.

Source validation, source-contract validation, data quality and final-handoff generation
were rerun after the attempts. No raw payload was added to Git.

## Recommended options and contingencies

1. Historical sources: acquire only after source-specific licence review; otherwise retain
   metadata, URLs, checksums when available and explicit unavailable receipts.
2. CMS CLFS: retain only demonstrably permitted numeric derived fields and exclude CPT/HCPCS
   identifiers and descriptor text; keep the source private if permission is uncertain.
3. Hugging Face: publish only the approved derived bundle after credentials and explicit
   dispatch; retain dry-run state if credentials or evidence gates fail.
4. Zenodo: create a draft without publication or DOI reservation; preserve the deposition
   manifest if the token-gated mutation cannot run.
5. OSF: synchronize protocol/report metadata while preserving immutable registration `gqk4z`
   and recording post-registration evolution; do not overwrite the registration.

Papers and preprints remain excluded from all options.
