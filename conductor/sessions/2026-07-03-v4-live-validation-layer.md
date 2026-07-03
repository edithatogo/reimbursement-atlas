# Session: v4 live-validation layer

Date: 2026-07-03

## Summary

Implemented a v4 pass focused on moving from design-only/no-network fixtures toward reviewed live-source validation without committing raw restricted data.

## Added

- PBS, CMS ASP and CMS PFS parser prototypes.
- Fixtures for PBS, CMS ASP and CMS PFS.
- Six source-version records and six fixture snapshot records.
- `src/reimburse_atlas/local_sources.py` for checksum snapshots and local parse operations.
- CLI commands: `source-status`, `snapshot-local-file`, `parse-local-source`.
- Crosswalk review queue generation.
- `data/seed/source_status.*` with current first-wave source observations.
- Public data policy checker to prevent raw/local cache paths from being tracked.
- Live-source validation playbook and ADRs 0009/0010.

## Generated counts after refresh

- 60 source registry rows.
- 25 analysis catalogue rows.
- 14 ontology rows.
- 6 source-version records.
- 6 source-snapshot records.
- 5 source-status records.
- 10 vertical-slice schedule items.
- 2 vertical-slice coverage decisions.
- 4 crosswalk candidates and 4 review-queue rows.

## Next

Manually download and validate one MBS descriptor/item-map pair and one CMS CLFS file. Do not commit raw files. Record checksums and parse only dashboard-safe derived records.
