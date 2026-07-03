# Session: snapshot/provenance gate

Date: 2026-07-03

## Added

- `SourceSnapshotRecord` schema export.
- `src/reimburse_atlas/snapshots.py` for checksum/provenance records.
- `source-snapshots` CLI command.
- `scripts/make_source_snapshots.py`.
- `data/seed/source_snapshots.*` generated from committed synthetic fixtures.
- Seed-lake materialisation now includes `source_snapshots` when present.
- Dashboard-safe CSV sync now copies `source_snapshots.csv`.

## Validation

Local validation after this pass:

```text
41 passed, 4 skipped
```

## Next recommended move

Use the snapshot gate for one manually downloaded MBS descriptor/item-map release and one CMS
CLFS public file. Do not commit raw files until licence and redistribution
review is explicitly recorded.
