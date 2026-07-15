# Reviewed source bundles

A reviewed source bundle is the v5 bridge between synthetic fixtures and live public source validation.

It exists so maintainers can manually download a public schedule file into an ignored local cache, parse it, and keep only derived, reviewable artefacts under version control or release review.

## Invariant

Raw files are **not copied** into the bundle. The bundle contains:

- `source_snapshots.jsonl` and `source_snapshots.csv` with checksum, byte size and licence/cache scope;
- derived normalised schedule or coverage rows;
- `validation_report.json`;
- `publication_manifest.json` for bundle-local publication review.

## Example

```bash
PYTHONPATH=src reimbursement-atlas reviewed-source-bundle \
  --source-version-id au_pbs_seed_fixture \
  --content-type text/csv \
  tests/fixtures/pbs_fixture.csv
```

For real reviewed files, place the raw file under an ignored path such as `data/raw_live/au_pbs/` and run the same command against that path.

## MBS TXT pair support

MBS TXT validation uses a paired command because the item-map and descriptor files are separate:

```bash
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
```

See `docs/MBS_REVIEWED_PAIR_BUNDLE.md` for the pair-specific join and validation contract.

## Publication rule

Bundle outputs are not automatically publishable. A reviewer must confirm:

1. the source-specific licence allows derived redistribution;
2. bundle snapshot files keep `local_path` redacted;
3. restricted descriptors, CPT text, UMLS/RxNorm dumps, DSM-5 text or confidential net prices are not included;
4. coverage is not inferred from price-file presence.

Nested reviewed-bundle files are automatically enumerated by the publication manifest and data
dictionary. They remain `public_reuse_review` candidates until the source-specific licence gate
is approved.
