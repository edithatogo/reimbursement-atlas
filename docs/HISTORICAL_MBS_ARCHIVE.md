# Historical MBS Archive

The project maintains a metadata-only inventory of historical MBS download
targets in:

- `data/seed/historical_mbs_archive_targets.jsonl`
- `data/derived/historical_sources/`

The current inventory was refreshed from the official MBS archive index pages
and contains 343 targets across 32 archive pages, spanning releases from 1974
through 2026. It records official URLs, archive pages, file names and periods;
it does not contain the source PDFs, TXT files or other raw payloads.

Refresh the inventory when network access is available:

```bash
PYTHONPATH=src python scripts/make_historical_source_index.py --refresh
```

The default deterministic command only regenerates the derived CSV, JSONL and
summary from the committed metadata seed:

```bash
pixi run historical-sources
```

Every target remains `manual_review_only` and `public_reuse_review`. The
inventory is not evidence that a file may be downloaded, parsed or republished.
Before acquiring a target, record source-specific terms, download it only into
ignored `data/raw_live/`, snapshot its checksum and promote only permitted
derived fields through the source-contract and reviewed-bundle gates.

The scheduled `.github/workflows/historical-source-inventory.yml` workflow refreshes this
metadata-only inventory and opens a normal PR when official archive pages change. It never
downloads historical payloads, bypasses licence review or writes directly to `main`.
