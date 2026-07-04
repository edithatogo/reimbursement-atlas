# Current focus

The repo is now in the first executable vertical-slice plus reviewed-source-bundle phase, with v7 adding installed Python and Node quality gates plus a build-tested dashboard.

## Immediate focus

1. Keep all public artefacts dashboard-safe and licence-safe.
2. Mature fixture-backed parsers for MBS, PBS, CMS CLFS, CMS PFS, CMS ASP and NHS genomic test directory records.
3. Add live-source validation only through manually reviewed local cache/provenance gates and reviewed-source bundles.
4. Use readiness tables to prioritise analyses and sources rather than broadening ingestion prematurely.
5. Keep CLI/API/MCP surfaces read-only until acquisition and licence controls are mature.
6. Keep the Python quality gate green: Ruff, basedpyright, Bandit, compileall, uv build and >90% core library coverage.
7. Keep the dashboard lockfile/build gate green with `npm ci`, `npm audit` and `npm run build`.

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

## v7 dashboard and mutation artefacts

- `docs/DASHBOARD_VALIDATION.md`
- `docs/MUTATION_TESTING.md`
- `docs/ADRs/0015-locked-dashboard-build.md`
- `docs/ADRs/0016-mutmut-nightly-not-pr-blocker.md`
- `conductor/sessions/2026-07-04-v7-dashboard-node-and-mutation.md`

## v6 quality-gate artefacts

- `docs/LOCAL_TOOLCHAIN_VALIDATION.md`
- `docs/TEST_GOBLIN_COMPATIBILITY.md`
- `docs/COVERAGE_POLICY.md`
- `docs/ADRs/0013-installed-toolchain-and-quality-gates.md`
- `docs/ADRs/0014-defusedxml-for-local-source-validation.md`

## Next agent handoff

Start with `docs/LOCAL_TOOLCHAIN_VALIDATION.md`, `docs/DASHBOARD_VALIDATION.md`, `docs/MUTATION_TESTING.md`, `docs/COVERAGE_POLICY.md`, `docs/FIRST_EXECUTABLE_SLICE.md` and `docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md`, then inspect `scripts/make_vertical_slice.py`, `src/reimburse_atlas/parsers/`, `src/reimburse_atlas/local_sources.py`, `src/reimburse_atlas/analysis/` and `conductor/sessions/2026-07-04-v7-dashboard-node-and-mutation.md`.

## v8 source-file and external-gate artefacts

- `data/seed/source_files.*`
- `schema/SourceFileRecord.schema.json`
- `docs/EXACT_SOURCE_FILES.md`
- `docs/MBS_TXT_PAIR_PARSER.md`
- `docs/EXTERNAL_QUALITY_GATES.md`
- `docs/ADRs/0017-exact-source-file-records.md`
- `docs/ADRs/0018-external-quality-gates-are-classified.md`
- `conductor/sessions/2026-07-04-v8-source-files-and-external-gates.md`

Immediate next step: validate `parse-mbs-txt-pair` against manually downloaded July 2026 MBS TXT files in `data/raw_live/au_mbs/`, then create a reviewed-source bundle or derived-only reviewed output without committing raw files.
