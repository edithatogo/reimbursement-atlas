# Session: executable slice continuation

Date: 2026-07-03

## Goal

Continue from the design scaffold and previous development pass. Move the repository toward an executable design while preserving licence/provenance safety.

## Implemented

- Added first-wave parser prototypes:
  - `parse_mbs_xml`
  - `parse_cms_clfs_csv`
  - `parse_nhs_genomic_directory_csv`
- Added ingestion-planning records with network and licence gates.
- Added readiness-generation logic for sources and analyses.
- Added deterministic token-overlap crosswalk review queue.
- Added local vertical-slice generator.
- Added dashboard CSV sync and updated the Astro/Cosmograph graph component to load generated CSVs.
- Added optional read-only FastAPI scaffold.
- Added MCP read-only tool manifest.
- Added devcontainer and additional workflow scaffolds.
- Added docs:
  - `docs/FIRST_EXECUTABLE_SLICE.md`
  - `docs/API_MCP_CLI_PLAN.md`
  - ADR 0006 and ADR 0007
- Generated dashboard-safe artefacts and JSON schemas.

## Validation

Commands run locally:

```bash
PYTHONPATH=src python scripts/make_graph_seed.py
PYTHONPATH=src python scripts/make_readiness_tables.py
PYTHONPATH=src python scripts/make_ingestion_plan.py
PYTHONPATH=src python scripts/make_vertical_slice.py
PYTHONPATH=src python scripts/sync_dashboard_seed.py
PYTHONPATH=src python scripts/export_json_schema.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src scripts tests
```

Result:

```text
41 passed, 4 skipped
```

Skipped tests require optional packages such as DuckDB, Polars or Hypothesis in the active environment.

## Generated counts

- 60 source readiness rows.
- 25 analysis readiness rows.
- 3 first-wave ingestion tasks.
- 4 synthetic schedule-item records.
- 2 synthetic coverage-decision records.
- 4 synthetic crosswalk candidates.
- 3 source snapshot provenance records with SHA-256 checksums.

## Important caution

All vertical-slice schedule/coverage data are synthetic fixtures. They validate the architecture but should not be used as policy evidence.

## Next recommended moves

1. Consolidate duplicate parser/adapter fixture conventions.
2. Validate MBS parser against one locally downloaded MBS XML file.
3. Validate CMS CLFS parser against one locally downloaded public CLFS file while avoiding CPT descriptor redistribution.
4. Add `SourceSnapshotRecord` and local ignored cache rules.
5. Build the first Polars/DuckDB mart from parsed JSONL.
6. Add dashboard tables for readiness and crosswalk review queue.
