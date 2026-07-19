# Historical Source Archival and Reproducibility

The project archives historical source payloads locally so that future derived
records can be independently reproduced and cited. Local archival is not a
licence decision and does not authorise redistribution.

## BPML terminology

“BPML 2.0” is not the current recognised standards name. BPML was an older
Business Process Modeling Language; the current OMG standard is **BPMN 2.0**
(Business Process Model and Notation). The transformation process is therefore
represented as a non-executable BPMN 2.0 XML model at
`data/derived/processes/historical_source_transformation.bpmn`.

## Acquisition

Run `pixi run historical-sources` to refresh the official MBS archive inventory,
then run:

```bash
PYTHONPATH=src uv run --all-extras python scripts/download_historical_sources.py
```

The command uses HTTPS-only `curl`, retries transient failures, preserves
existing cache files by default, and stores payloads only under the ignored
`data/raw_live/historical_sources/` directory. Use `--dry-run` to generate a
plan without network requests and `--force` only when intentionally replacing a
local cache file.

## Per-file evidence

`data/derived/historical_sources/historical_source_downloads.jsonl` records, for
each target:

- official archive page and direct source URL;
- source/version identifier and citation key;
- retrieval status, relative ignored-cache path, byte size and SHA-256;
- licence gate and human review status;
- transformation-process reference.

The archive is academic evidence infrastructure, not a public mirror. A source
must have an explicit source-specific licence decision, permitted derived-field
scope, parser version, validation report and citation metadata before derived
outputs can be promoted for publication or OSF/Hugging Face release.
