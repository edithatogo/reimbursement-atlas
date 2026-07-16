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

Generate the first-wave URL and licence checklist alongside the acquisition pack:

```bash
pixi run source-url-licence-checklist
```

The checklist is written to `data/derived/source_url_licence_checklist/`. It binds each
source-file record to its exact URL, registry URL, acquisition mode and licence gate.
Both URL verification and licence review remain explicitly pending until a human
records authoritative evidence; generation does not grant permission to publish.

## First live validation target

1. Review the MBS downloads page and download the July 2026 item-map and descriptor TXT files.
2. Place them under `data/raw_live/au_mbs/`.
3. Run `reimbursement-atlas reviewed-mbs-txt-pair-bundle` to snapshot both files and emit a derived-only bundle.
4. Inspect `validation_report.json`, especially joined-row and descriptor-only-row counts.
5. Run `reimbursement-atlas publication-manifest` and `python scripts/check_public_data_policy.py`.

The same pattern should be used for CMS CLFS, PBS API/CSV, CMS ASP and CMS PFS once their licence gates
and descriptor-redistribution constraints have been reviewed.
