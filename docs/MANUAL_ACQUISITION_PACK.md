# Manual acquisition pack

The manual acquisition pack turns exact `SourceFileRecord` rows into a safe reviewed-source checklist.
It is deliberately not a downloader. Raw reimbursement schedule files may be public, but public does not
always mean redistributable, and several first-wave files pass through licence or descriptor gates.

Generate the pack:

```bash
pixi run manual-acquisition-pack
# or
PYTHONPATH=src python scripts/make_manual_acquisition_pack.py
```

Outputs:

- `data/derived/manual_acquisition_pack/acquisition_steps.jsonl`
- `data/derived/manual_acquisition_pack/acquisition_steps.csv`
- `data/derived/manual_acquisition_pack/README.md`
- `data/derived/manual_acquisition_pack/source_file_commands.sh`

Each row records the source URL, acquisition mode, licence gate, expected raw handling, suggested
ignored local path, snapshot command and parse command. The raw path convention is:

```text
data/raw_live/<source_id>/<file_name>
```

`data/raw_live/` is git-ignored. Commit only source metadata, checksums and derived rows.

## First live validation target

1. Review the MBS downloads page and download the July 2026 item-map and descriptor TXT files.
2. Place them under `data/raw_live/au_mbs/`.
3. Snapshot each file with `reimbursement-atlas snapshot-local-file`.
4. Parse the pair with `reimbursement-atlas parse-mbs-txt-pair`.
5. Run `reimbursement-atlas publication-manifest` and `python scripts/check_public_data_policy.py`.

The same pattern should be used for CMS CLFS, PBS API/CSV, CMS ASP and CMS PFS once their licence gates
and descriptor-redistribution constraints have been reviewed.
