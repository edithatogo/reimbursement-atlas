# Publication manifest

The v5 publication manifest is a candidate release manifest for GitHub releases, Hugging Face datasets and dashboard-safe derived exports.

It records, for each candidate artefact:

- relative path;
- file format;
- row count;
- byte size;
- SHA-256 checksum;
- publication scope;
- licence gate;
- whether the path appears to contain raw source payload.

Generate it with:

```bash
PYTHONPATH=src python scripts/make_publication_manifest.py
# or
PYTHONPATH=src reimbursement-atlas publication-manifest data/derived/publication_manifest.json
```

The manifest is deliberately conservative. Seed metadata and synthetic/derived vertical-slice outputs are publication candidates; raw and local cache paths are excluded.

Before publishing to Hugging Face, a maintainer should compare this manifest with:

- `docs/DATA_GOVERNANCE.md`;
- `docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md`;
- `data/seed/source_snapshots.*`;
- `data/seed/source_registry.*` licence notes.
## Research-package descriptor determinism

The generated Frictionless, RO-Crate and DCAT descriptors intentionally exclude
the descriptor files themselves from the publication manifest. This prevents a
descriptor from hashing its previous generation and makes repeated generation
byte-stable. The descriptors still carry checksums for the licence-reviewed
derived artefacts that they describe.
