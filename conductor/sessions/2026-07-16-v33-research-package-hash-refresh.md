# Conductor session: research-package hash refresh

## Scope

Close a generated-artifact consistency gap found during the final handoff replay.

## Evidence

- `data/derived/release_readiness/release_gates.jsonl` and `.csv` contained current hashes.
- `data/derived/research_package/datapackage.json` and `ro-crate-metadata.json` still contained the
  previous release-gate hashes.
- Running `pixi run research-package` refreshed both descriptor files.
- A second immediate `pixi run research-package` produced no further diff.

## Decision

Commit the descriptor refresh under `track_data_packaging_standards`; do not weaken the descriptor
self-reference exclusion or any evidence/publication readiness gate.
