# Current focus

The repo is now in the first executable vertical-slice plus reviewed-source-bundle phase, with v6 adding installed Python quality gates.

## Immediate focus

1. Keep all public artefacts dashboard-safe and licence-safe.
2. Mature fixture-backed parsers for MBS, PBS, CMS CLFS, CMS PFS, CMS ASP and NHS genomic test directory records.
3. Add live-source validation only through manually reviewed local cache/provenance gates and reviewed-source bundles.
4. Use readiness tables to prioritise analyses and sources rather than broadening ingestion prematurely.
5. Keep CLI/API/MCP surfaces read-only until acquisition and licence controls are mature.
6. Keep the Python quality gate green: Ruff, basedpyright, Bandit, compileall, uv build and >90% core library coverage.
7. Generate a dashboard package lock and run the Astro/Cosmograph build in a Node-ready environment.

## Current generated artefacts

- `data/seed/source_readiness.*`
- `data/seed/analysis_readiness.*`
- `data/seed/first_wave_ingestion_plan.*`
- `data/seed/source_status.*`
- `data/derived/vertical_slice/*`
- `data/derived/publication_manifest.json`
- `data/seed/analysis_recipes.*`
- `data/seed/ontology_concepts.*`
- `apps/dashboard/public/data/*`

## v6 quality-gate artefacts

- `docs/LOCAL_TOOLCHAIN_VALIDATION.md`
- `docs/TEST_GOBLIN_COMPATIBILITY.md`
- `docs/COVERAGE_POLICY.md`
- `docs/ADRs/0013-installed-toolchain-and-quality-gates.md`
- `docs/ADRs/0014-defusedxml-for-local-source-validation.md`

## Next agent handoff

Start with `docs/LOCAL_TOOLCHAIN_VALIDATION.md`, `docs/COVERAGE_POLICY.md`, `docs/FIRST_EXECUTABLE_SLICE.md` and `docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md`, then inspect `scripts/make_vertical_slice.py`, `src/reimburse_atlas/parsers/`, `src/reimburse_atlas/local_sources.py`, `src/reimburse_atlas/analysis/` and `conductor/sessions/2026-07-03-v6-installed-toolchain-quality-gates.md`.
