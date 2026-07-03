# Data governance

## Data zones

| Zone | Tracked? | Contents |
|---|---:|---|
| `data/seed/` | Yes | Permissive metadata, registries, graph seeds and placeholders. |
| `data/raw/` | No | Downloaded source files, restricted data, live extracts and licence-bound files. |
| `data/raw_live/` | No | Manually downloaded first-wave validation files. |
| `data/processed/` | No | Parser outputs, Parquet/Arrow snapshots and local analysis marts. |
| `data/public/` | Optional | Reviewed, permissive derived datasets for Hugging Face. |
| `lancedb/` | No | Local vector databases generated from permitted text. |

## Provenance fields

Every source version should eventually include:

- source id;
- URL;
- retrieval timestamp;
- effective date;
- publication date;
- checksum;
- content type;
- parser version;
- licence class;
- raw file path;
- row count;
- validation status;
- reviewer.

## Public release rules

A dataset can be pushed to Hugging Face only if:

1. every row is derived from a source with permissive redistribution or is original metadata;
2. restricted identifiers are allowed;
3. no proprietary descriptors or confidential prices are included;
4. licence and attribution are included in the dataset card;
5. checksums and provenance are reproducible;
6. review status is recorded;
7. `scripts/check_public_data_policy.py` confirms no ignored raw/local cache paths are tracked.

## Privacy

The design phase uses public schedules and should not contain patient-level data. Future patient-level or claims-level analysis must use separate governance, ethics and secure compute arrangements.


## Live-source validation

Live public files should be handled as local raw evidence first. A reviewer should download the file, create a `SourceSnapshotRecord`, parse into derived rows, then decide whether the raw file can ever be mirrored. The default cache scope for first-wave validation is `local_raw_only` for raw inputs and `public_derived_only` for parsed outputs.

## v5 publication-manifest gate

Before exporting any public dataset, run:

```bash
PYTHONPATH=src reimbursement-atlas validate-seed-files
PYTHONPATH=src python scripts/check_public_data_policy.py
PYTHONPATH=src reimbursement-atlas publication-manifest data/derived/publication_manifest.json
```

The publication manifest records candidate artefacts, row counts, checksums and conservative licence gates. Raw/local-cache paths are excluded. A human reviewer must still approve source-specific redistribution terms before Hugging Face publication.
