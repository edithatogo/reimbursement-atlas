# MBS reviewed TXT-pair bundle

The MBS July 2026 historical TXT workflow is a **two-file acquisition**:

- item-map TXT: item code, group/category and payment-like fields;
- descriptor TXT: item code and descriptor text.

The atlas therefore treats MBS TXT validation as a paired source, not as two independent one-file parses.

## Command

```bash
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT \
  --output-dir data/derived/reviewed_source_bundles
```

The command:

1. snapshots both local raw files by checksum and byte size;
2. redacts local raw paths from the bundle snapshot table;
3. joins descriptors to item-map rows by MBS item code;
4. emits derived `ScheduleItemRecord` JSONL/CSV rows;
5. writes a validation report with item-map, descriptor, joined and descriptor-only row counts;
6. writes a bundle-local publication manifest.

## Safety invariant

Raw TXT files are never copied into the bundle. The committed artefacts should be derived-only and should not contain private filesystem paths.

The bundle validation report deliberately warns when descriptor-only rows exist. Those rows are useful for parser diagnostics but usually need review before policy analysis because they may lack payment fields from the item map.

The current local July 2026 acquisition produced 14,856 rows: 14,854 joined item-map rows and
2 descriptor-only rows. The committed bundle records both source checksums, but its
`licence_gate` remains `public_reuse_review`; this is a review packet, not an approved public
dataset.

## Why this matters

A naive single-file parser would either drop descriptors or treat descriptor-only rows as priced schedule items. The paired bundle makes the join explicit and records enough provenance to support review before any MBS/CMS comparison.
