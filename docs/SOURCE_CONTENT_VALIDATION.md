# Source content validation

The source-download layer now has a separate post-download validation step. This deliberately happens after `curl`/`wget` acquisition and before any reviewed-source bundle or parser step.

The validator reads `data/seed/source_files.jsonl`, locates the expected ignored local target under `data/raw_live/`, and emits dashboard-safe metadata only:

- source-file id, source id and source-version id;
- validation status: `pass`, `warn`, `fail`, `missing` or `skipped`;
- expected format and expected/observed record count where available;
- byte size and checksum for local files;
- a redacted `local_raw_only:<source>/<filename>` reference rather than an absolute path;
- issues and recommended next action.

Licence-gated, landing-page, metadata-only and manual-extract records are marked `skipped` rather than auto-downloaded or parsed. Missing executable public-download candidates are marked `missing`, which is expected in offline sandboxes and actionable in network-enabled CI/local environments.

Run:

```bash
PYTHONPATH=src reimbursement-atlas source-validation
# or
PYTHONPATH=src python scripts/make_source_validation.py
```

Generated artefacts:

```text
data/derived/source_validation/source_content_validation.jsonl
data/derived/source_validation/source_content_validation.csv
data/derived/source_validation/summary.json
```

This gate is intentionally conservative: it checks for common failure modes such as empty downloads, HTML error pages saved as `.TXT`, invalid JSON/ZIP structure and large deviations from expected record counts. The optional `pixi run local-parser-contracts` gate validates the MBS TXT pair and PBS API/CSV parser contracts against ignored local caches when those caches are present. It emits only redacted paths, checksums, counts and boolean checks; it never writes raw payloads, performs network I/O or changes licence/evidence readiness. With no local cache it reports `skipped`. Passing this local contract gate is parser evidence only, not human source review or publication approval.
