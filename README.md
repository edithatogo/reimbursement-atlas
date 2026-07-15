# Reimbursement Atlas Conductor

[![CI](https://github.com/edithatogo/reimbursement-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/reimbursement-atlas/actions/workflows/ci.yml)
[![Dashboard build](https://github.com/edithatogo/reimbursement-atlas/actions/workflows/dashboard-preview.yml/badge.svg)](https://github.com/edithatogo/reimbursement-atlas/actions/workflows/dashboard-preview.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

A design-first repository for comparing public reimbursement schedules across US CMS, Australian MBS/PBS, and other public billing, tariff, drug, diagnostic, hospital and coverage-decision systems.

This repository has moved from a design scaffold into a first executable, no-network vertical slice. It defines the context-management layer, policy requirements, source registry, analysis catalogue, ontology strategy, test strategy, dashboard architecture and automation plan, and now includes parser prototypes, readiness tables, reviewed-source bundle tooling, redacted MBS TXT-pair bundle support, publication manifests and generated vertical-slice artefacts.

## Current public status

The public product is a reproducible software and metadata surface, not a claim that every
research question is evidence-ready. The current product is **not evidence-ready** for policy
claims. The static dashboard presents source, mapping, analysis, automation and release-readiness
metadata generated from tracked seeds and derived artefacts. Live-source acquisition, licence
review, human mapping adjudication, human research review, protocol registration and external
publication remain explicit gates. See [`apps/dashboard/public/status.json`](apps/dashboard/public/status.json)
for the machine-readable status contract and [`CITATION.cff`](CITATION.cff) for citation metadata.
Human and external release decisions are tracked in [`docs/REVIEW_DECISIONS.md`](docs/REVIEW_DECISIONS.md).
Consumers can verify tagged release provenance using [`docs/RELEASE_VERIFICATION.md`](docs/RELEASE_VERIFICATION.md).

Software and project-owned documentation are licensed under Apache-2.0. Underlying source data
retain their own provider licences and are not relicensed by this repository; CMS/AMA terms apply
to CMS CLFS/PFS material. Raw live-source payloads remain local and ignored.

Public dashboard: [GitHub Pages](https://edithatogo.github.io/reimbursement-atlas/) or run
`pixi run dashboard-build` locally. GitHub Pages and Hugging Face
publication workflows are manual and token/approval-gated.

## Why this exists

Public reimbursement schedules encode policy choices: what gets paid, who can access it, what is bundled, what is restricted, what is visible, and what remains hidden behind local discretion, negotiated rebates or confidential deeds.

The atlas is designed to answer questions like:

- How do selected, matched schedule-amount relativities differ between procedural and cognitive care?
- Does public genomic test coverage translate into diffusion?
- Which systems are transparent versus merely public?
- Where do coverage restrictions create inequity or access delays?
- Which prices are comparable, and which are artefacts of bundling?
- Which ontologies are needed to make cross-jurisdictional mappings credible?

## Repository shape

```text
.
├── conductor/                 # Context management system for future agents
├── docs/                      # Requirements, sources, analyses, governance, roadmap
├── data/seed/                 # Permissively shareable seed registries and graph files
├── src/reimburse_atlas/       # Typed contracts, parsers, readiness, ingestion and API scaffolds
├── tests/                     # Unit, property, integration, e2e and smoke tests
├── apps/dashboard/            # Astro 7 + Cosmograph dashboard scaffold
├── mojo/                      # Mojo design notes and future kernels
├── schema/                    # Generated JSON schema targets
├── .github/                   # Actions, templates, security and automation
└── infra/huggingface/         # Dataset/Space publishing scaffold
```

## Initial stack

- Python 3.14-primary orchestration package with Pydantic v2, Polars, Arrow, DuckDB and LanceDB; Python 3.13 is only a compatibility fallback for environments where 3.14 is unavailable.
- Pixi for reproducible multi-environment development.
- uv/uv_build for Python package builds.
- Ruff in strict, preview-heavy mode; basedpyright in strict mode.
- Pytest, Hypothesis, mutmut, Scalene, Bandit and pip-audit, now install-tested through `uv` for the Python core.
- Astro 7 dashboard using Cosmograph for graph exploration, with a committed npm lockfile, current-channel dependency updates and local static build validation.
- Mojo-first performance-kernel track for high-throughput parsers, fixed-width tokenisation, similarity kernels and mapping accelerators; Python remains the orchestration/interface layer.

## Current seed and generated assets

- `data/seed/source_registry.*`: 60 public or partly public schedule/source families.
- `data/seed/analysis_catalogue.*`: 25 policy-relevant analyses.
- `data/seed/ontology_registry.*`: ontology/licensing/mapping strategy.
- `data/seed/ontology_concepts.*` and `ontology_mapping_templates.*`: synthetic local-only terminology workflow seeds.
- `data/seed/analysis_recipes.*`: workflow-ready MoSCoW-style analysis recipes and quality gates.
- `data/seed/source_versions.*`: first-wave source-version and parser-target fixtures.
- `data/seed/source_status.*`: current public-source observations and recommended acquisition actions.
- `data/seed/graph_nodes.csv` and `data/seed/graph_edges.csv`: generated graph for Cosmograph.
- `data/seed/source_readiness.*` and `data/seed/analysis_readiness.*`: generated readiness tables.
- `data/seed/first_wave_ingestion_plan.*`: generated parser/source-version task tables.
- `data/seed/source_acquisition_plan.*` and `data/seed/ingestion_readiness.*`: licence-gated acquisition/readiness tables.
- `data/derived/vertical_slice/*`: generated no-network parser/crosswalk/policy-signal demonstration artefacts.
- `data/seed/source_snapshots.*`: checksum/provenance records for committed synthetic fixtures.
- `data/derived/seed_lake/*`: local JSONL/CSV lake materialisation and manifest.
- `data/derived/publication_manifest.json`: candidate public/Hugging Face dataset publication manifest.
- `data/derived/toolchain_report.*`: local installed-toolchain availability report.
- `data/derived/v6_validation_run.json` and `v7_validation_run.json`: local validation-run summaries.
- `apps/dashboard/public/data/*`: dashboard-safe generated CSV copies.
- `apps/dashboard/package-lock.json`: locked Node dependency graph for CI and Hugging Face Space builds.
- `schema/`: generated from Pydantic models after running `pixi run schema-export`.

## First local commands

```bash
pixi install
pixi run seed-validate
pixi run public-data-policy
pixi run graph-seed
pixi run readiness
pixi run ingestion-plan
pixi run acquisition-plan
pixi run vertical-slice
pixi run source-snapshots
pixi run source-validation
pixi run ontology-seed
pixi run seed-sync
pixi run seed-sync-check
pixi run publication-manifest
pixi run roadmap-linkages
pixi run data-quality
pixi run toolchain-report
pixi run seed-lake
pixi run dashboard-seed
pixi run qa
pixi run dashboard-build
pixi run dashboard-dev
```

Without Pixi:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src pytest tests/unit tests/smoke -q
```

Installed-toolchain path used in v6:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e '.[dev,api,mcp,test-goblin]'
PYTHONPATH=src ruff check .
PYTHONPATH=src ruff format --check .
PYTHONPATH=src basedpyright
PYTHONPATH=src pytest --cov=src/reimburse_atlas --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -q
PYTHONPATH=src bandit -q -c pyproject.toml -r src scripts
uv build
```


## Current executable commands

```bash
PYTHONPATH=src reimbursement-atlas validate
PYTHONPATH=src reimbursement-atlas score-sources
PYTHONPATH=src reimbursement-atlas source-status
PYTHONPATH=src reimbursement-atlas readiness data/seed
PYTHONPATH=src reimbursement-atlas ingestion-plan data/seed
PYTHONPATH=src reimbursement-atlas acquisition-plan data/seed
PYTHONPATH=src reimbursement-atlas vertical-slice data/derived/vertical_slice
PYTHONPATH=src reimbursement-atlas source-snapshots data/seed
PYTHONPATH=src reimbursement-atlas source-validation
PYTHONPATH=src reimbursement-atlas roadmap-linkages
PYTHONPATH=src reimbursement-atlas data-quality
PYTHONPATH=src reimbursement-atlas snapshot-local-file --source-version-id au_pbs_seed_fixture tests/fixtures/pbs_fixture.csv --content-type text/csv
PYTHONPATH=src reimbursement-atlas parse-local-source --source-version-id au_pbs_seed_fixture tests/fixtures/pbs_fixture.csv
PYTHONPATH=src reimbursement-atlas reviewed-source-bundle --source-version-id au_pbs_seed_fixture --content-type text/csv tests/fixtures/pbs_fixture.csv
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle tests/fixtures/mbs_txt/20260701_MBSONLINE_IMAP_fixture.TXT tests/fixtures/mbs_txt/20260701_MBSONLINE_DESC_fixture.TXT
PYTHONPATH=src reimbursement-atlas validate-seed-files
PYTHONPATH=src reimbursement-atlas publication-manifest data/derived/publication_manifest.json
PYTHONPATH=src reimbursement-atlas seed-lake data/derived/seed_lake
PYTHONPATH=src reimbursement-atlas export-graph data/seed
PYTHONPATH=src reimbursement-atlas snapshot
```

The first development slice now focuses on MBS, PBS, CMS CLFS, CMS PFS, CMS ASP and the NHS genomic test directory, emitting typed `ScheduleItemRecord`, `CoverageDecisionRecord` and `CrosswalkCandidate` objects before any broader ingestion work.

## Design stance

The project should stay design-led until the following are mature:

1. source registry and licence gating;
2. ontology and terminology strategy;
3. crosswalk model;
4. first-wave analysis definitions;
5. dashboard information architecture;
6. GitHub project automation and issue taxonomy;
7. reproducible extract-transform-load conventions.

No restricted ontology dumps, proprietary code-system descriptors, UMLS data, CPT text, DSM-5 text or confidential drug pricing data should be committed.

Typed contracts now cover provenance, schedule items, coverage decisions and crosswalk candidates. Parser development should target those contracts before live ingestion.


## Implementation status after the current pass

- First-wave parser prototypes: MBS XML-like, PBS CSV-like, CMS CLFS CSV-like, CMS PFS CSV-like, CMS ASP CSV-like and NHS genomic-directory-like fixtures.
- Generated local vertical slice: 10 schedule items, 2 coverage decisions, 4 candidate crosswalk records, 4 review-queue rows and 6 policy-signal rows from synthetic fixtures.
- Generated fixture snapshot records: 6 checksum/provenance rows to gate future live-source validation.
- Generated source-status observations: 5 current public-source acquisition notes for MBS, PBS, CLFS, PFS and ASP.
- Generated readiness artefacts: 60 source rows and 25 analysis rows.
- API scaffold: optional read-only FastAPI factory in `src/reimburse_atlas/api.py`.
- MCP scaffold: read-only tool manifest in `mcp/tools.seed.json` plus a lazy optional server in `src/reimburse_atlas/mcp_server.py`.
- Dashboard now loads generated CSV files from `apps/dashboard/public/data/`, including source status, analysis recipes, ontology concepts, crosswalk review queue and policy-signal outputs.

The generated demonstration data are synthetic and intended to test the system design. Live-source ingestion remains gated behind licence/provenance review.


## Optional API and MCP surfaces

The core package remains usable without FastAPI or the MCP SDK. The optional surfaces are lazy-imported and read-only:

```bash
pixi run -e api api-dev
pixi run -e mcp mcp-dev
```

The MCP dependency is constrained to the stable 1.x line for now; live fetching, restricted ontology access and write operations remain out of scope until licence/provenance gates are production-ready.



## v6 installed-toolchain and quality-gate layer

The v6 pass installed and exercised the Python development stack locally rather than leaving it as CI-only scaffolding. The core package now passes Ruff, Ruff format check, basedpyright strict type checking, Bandit, `compileall`, `uv build`, and a 90% coverage gate over the core library.

The `test-goblin` extra is now a compatibility profile built from Hypothesis, mutmut and pytest-randomly. This keeps the intended goblin-style adversarial testing direction without depending on an unresolved placeholder package.

See:

- `docs/LOCAL_TOOLCHAIN_VALIDATION.md`
- `docs/TEST_GOBLIN_COMPATIBILITY.md`
- `docs/COVERAGE_POLICY.md`

## v5 reviewed-source and publication layer

The current pass adds a safer path from synthetic fixtures to real public-source validation:

```bash
PYTHONPATH=src reimbursement-atlas reviewed-source-bundle \
  --source-version-id au_pbs_seed_fixture \
  --content-type text/csv \
  tests/fixtures/pbs_fixture.csv

PYTHONPATH=src reimbursement-atlas validate-seed-files
PYTHONPATH=src reimbursement-atlas publication-manifest data/derived/publication_manifest.json
```

The reviewed-source bundle writes checksum metadata, derived rows, validation reports and a bundle-local publication manifest without copying the raw file. This is the intended workflow for manually downloaded MBS, PBS, CMS and NHS source files.


## v7 dashboard and Node validation layer

The v7 pass installed the dashboard dependencies, generated `apps/dashboard/package-lock.json`, changed dashboard CI to `npm ci`, and made the Astro/Cosmograph dashboard build locally. The dashboard now has static routes for sources, analyses, crosswalks, ontologies and readiness tables, all reading from dashboard-safe generated CSV artefacts.

The build uses a local Astro config alias for `gl-bench` so Cosmograph works under the Astro 7 / Vite 8 / Rolldown path without patching package files.

Validated commands now include:

```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest --cov=src/reimburse_atlas --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -q
uv run bandit -q -c pyproject.toml -r src scripts
uv build
cd apps/dashboard && npm ci && npm audit --omit=dev --audit-level=moderate && npm run build
```

`pip-audit` is installed but remained blocked here by DNS resolution to `pypi.org`. Full mutmut is now wired correctly, but the configured run generated 3,673 mutants across 45 files and should remain a scheduled/manual gate rather than a fast PR blocker.

See:

- `docs/DASHBOARD_VALIDATION.md`
- `docs/MUTATION_TESTING.md`
- `docs/ADRs/0015-locked-dashboard-build.md`
- `docs/ADRs/0016-mutmut-nightly-not-pr-blocker.md`

## v8 source-file and external-gate layer

The v8 pass adds an exact source-file acquisition layer and an MBS TXT-pair parser for the current item-map/descriptor file pattern.

New commands:

```bash
PYTHONPATH=src reimbursement-atlas source-files
PYTHONPATH=src reimbursement-atlas parse-mbs-txt-pair \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
PYTHONPATH=src python scripts/run_external_quality_gates.py
```

New public metadata outputs:

- `data/seed/source_files.*`
- `schema/SourceFileRecord.schema.json`
- `data/derived/external_quality_gates.*`
- `apps/dashboard/public/data/source_files.csv`
- `apps/dashboard/public/data/external_quality_gates.csv`

The external quality gate report distinguishes installed-but-network-blocked gates from missing tools. In the current runtime, `pip-audit` is installed but blocked by DNS access to `pypi.org`; `npm audit` passes; Pixi and Mojo executables are not present on `PATH`.

See:

- `docs/EXACT_SOURCE_FILES.md`
- `docs/MBS_TXT_PAIR_PARSER.md`
- `docs/EXTERNAL_QUALITY_GATES.md`
- `docs/ADRs/0017-exact-source-file-records.md`
- `docs/ADRs/0018-external-quality-gates-are-classified.md`


## v10 redacted MBS TXT-pair bundle layer

The v10 pass hardens reviewed-source bundles for publication review and adds a dedicated two-file MBS TXT workflow. Bundle snapshot exports now redact `local_path` so private raw-cache paths do not leak into derived artefacts. The MBS TXT-pair command snapshots both the item-map and descriptor files, joins them by MBS item code, emits derived `ScheduleItemRecord` rows, and writes pair-specific validation statistics.

New command:

```bash
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT \
  --output-dir data/derived/reviewed_source_bundles
```

See:

- `docs/MBS_REVIEWED_PAIR_BUNDLE.md`
- `docs/ADRs/0021-redacted-reviewed-source-bundles-and-mbs-pairing.md`

## v9 optional toolchain, acquisition-pack and mapping-workbench layer

The v9 pass adds three practical next-step layers:

1. **Optional toolchain probes** that distinguish `passed`, `blocked_network`, `missing_tool` and `wrong_tool`. Mojo now probes successfully via `uv tool run --from mojo-compiler mojo --version`. Pixi is only accepted if the official Prefix.dev executable is available; a wrong same-named PyPI executable is explicitly classified as `wrong_tool`.
2. **Manual acquisition pack** generation from exact source-file records. This creates a human-reviewed checklist, snapshot commands and parse commands while keeping raw files under ignored `data/raw_live/` paths.
3. **Mapping workbench** outputs, including a deterministic mapping evidence matrix and vector seed files for future Arrow/LanceDB-backed candidate search.

New commands:

```bash
pixi run manual-acquisition-pack
pixi run optional-toolchains
pixi run vector-seed
PYTHONPATH=src reimbursement-atlas manual-acquisition-pack
PYTHONPATH=src reimbursement-atlas vector-seed --build-lance
```

Generated v9 artefacts include:

- `data/derived/manual_acquisition_pack/*`
- `data/derived/vertical_slice/mapping_evidence_matrix.*`
- `data/derived/vector_seed/schedule_item_vectors.*`
- `data/derived/optional_toolchain_installs.*`
- `schema/MappingEvidenceRecord.schema.json`

See `docs/MANUAL_ACQUISITION_PACK.md`, `docs/MAPPING_WORKBENCH.md`, and `docs/OPTIONAL_TOOLCHAIN_INSTALLS.md`.

## v11 CI/CD and supply-chain hardening

The repository now treats GitHub automation as a first-class, dashboard-visible dataset. New generated artefacts include workflow-use scanning, workflow policy observations, automation controls, an action SHA-pinning queue, and minimal CycloneDX-style SBOMs for Python and the Astro dashboard.

Key commands:

```bash
PYTHONPATH=src uv run reimbursement-atlas repo-automation
PYTHONPATH=src uv run reimbursement-atlas sbom
PYTHONPATH=src uv run python scripts/run_external_quality_gates.py
```

The release workflow includes GitHub artifact attestation hooks for Python distributions, source archives and generated SBOMs. All workflow action references are currently pinned to full commit SHAs; `data/derived/repo_automation/action_sha_pin_plan.csv` is retained as a deterministic drift check and currently contains no unresolved migrations. Publication and evidence gates remain separate from software-release provenance.


## v13 architecture and release-readiness layer

The repository now emits architecture and release-readiness evidence as first-class artefacts:

```bash
pixi run architecture-report
pixi run release-readiness
PYTHONPATH=src reimbursement-atlas architecture-report
PYTHONPATH=src reimbursement-atlas release-readiness --allow-blockers
```

Architecture checks scan internal `reimburse_atlas` imports, enforce the `foundation -> parsing -> analysis -> orchestration -> interface` boundary model and report import cycles. Release readiness consolidates local quality gates, external quality-gate classification, workflow policy, SBOMs, dashboard build, public-data policy and publication manifests.

Current status: local quality, architecture, public-data, workflow-policy, SBOM and action-pinning checks pass. The software repository is release-ready. Evidence publication, OSF registration, Hugging Face publication, Zenodo DOI creation and policy claims remain fail-closed pending source/licence review, protocol approval and accountable human sign-off.

Zenodo metadata preparation is validated locally with `pixi run zenodo-metadata`; this does not
create a Zenodo record or DOI. See [`docs/ZENODO_RELEASE_PREPARATION.md`](docs/ZENODO_RELEASE_PREPARATION.md).

## v14 roadmap, OSF, Hugging Face, Mojo and acquisition layer

The v14 pass records the expanded roadmap as executable repo artefacts rather than prose. New seed registries now cover Conductor tracks, roadmap functions, dataset candidates, mapping resources, research questions, output artefact plans and runtime targets. The generated GitHub issue backlog expands those records into 94 issue drafts so that unfinished functions, datasets, outputs and quality tracks can be moved into GitHub Issues/Projects when the remote repository is available.

The runtime target is Mojo-first for high-throughput kernels and Python 3.14 for orchestration, validation, packaging and interfaces. The current environment validates the Python path under official Pixi Python 3.14.6 and uv Python 3.14.5; Python 3.13 remains a compatibility fallback. A small Mojo smoke kernel is included in `mojo/fixed_width_tokenizer.mojo` and can be run with:

```bash
bash scripts/run_mojo_smoke.sh
```

Source acquisition is now executable. The `source-download-plan` command emits curl/wget/API-style commands for exact source-file records, writes download plans and records attempted downloads without committing raw files:

```bash
PYTHONPATH=src reimbursement-atlas source-download-plan --attempt --method curl
```

In this sandbox, public MBS/PBS download attempts were classified as `blocked_network` because DNS resolution failed. This is recorded in `data/derived/source_downloads/download_attempts.*`; it is not treated as evidence that the sources are unavailable.

OSF is now part of the research workflow. The repo generates an OSF component plan, protocol/report scaffolds, and a token-gated workflow for future OSF publication. Hugging Face publication is also explicit: the workflow now has separate gated jobs for publishing the derived dataset and deploying the Astro dashboard to a Hugging Face Space.

Research packaging now emits Frictionless-style `datapackage.json`, RO-Crate metadata and DCAT JSON-LD under `data/derived/research_package/`.

New commands:

```bash
PYTHONPATH=src reimbursement-atlas roadmap
PYTHONPATH=src reimbursement-atlas runtime-targets
PYTHONPATH=src reimbursement-atlas research-map
PYTHONPATH=src reimbursement-atlas source-download-plan --attempt --method curl
PYTHONPATH=src python scripts/make_osf_plan.py
PYTHONPATH=src python scripts/make_research_package.py
```

## v15 additions

The v15 pass adds two further implementation gates before live-source ingestion expands:

- **Hardened source downloads**: generated `curl`/`wget` commands now use shell quoting, retries, resume support, HTTP header sidecars and ETag sidecars, while refusing to execute metadata-only, landing-page or licence-gated records.
- **Protocol status gate**: `reimbursement-atlas protocol-status` checks every registered research question against its protocol/report files and writes OSF-readiness evidence to `data/derived/protocols/`.

The dashboard now exposes protocol status and executable download-plan metadata. Generated GitHub issue drafts include the new download-hardening, protocol-completeness, checksum-pinning and source-validator work items.


## v16 evidence-readiness layer

The v16 pass adds three release-facing evidence gates:

- `source-validation`: validates downloaded source files under ignored `data/raw_live/` paths without exposing raw payloads or absolute local paths.
- `data-quality`: checks row counts, unique ids, referential integrity, generated artefact presence and publication-manifest raw-payload safety.
- `roadmap-linkages`: links every research question to registered sources, dataset candidates, mapping resources and output artefacts for OSF/GitHub Project planning.

These gates are visible in the dashboard, seed lake, publication manifest, release-readiness matrix and generated GitHub issue drafts.
### v17 evidence-readiness additions

The repository now generates three additional release-review artefacts:

```bash
PYTHONPATH=src reimbursement-atlas evidence-readiness
PYTHONPATH=src reimbursement-atlas source-drift
PYTHONPATH=src reimbursement-atlas data-dictionary
```

These produce research-question readiness rows, source/schema drift checks and a public artefact data dictionary for GitHub/Hugging Face/OSF/Zenodo review. All five initial research questions are currently prototype-ready, but still require real reviewed-source bundles and human mapping/preregistration review before policy claims are evidence-ready.


## v18 handoff gates

The latest design pass adds three final local-continuation artefacts:

```bash
PYTHONPATH=src reimbursement-atlas source-contracts
PYTHONPATH=src reimbursement-atlas github-project-export
PYTHONPATH=src reimbursement-atlas final-handoff
```

These produce source-specific parser contract checks, GitHub Project import rows and a final environment-dependent handoff checklist. Use `data/derived/final_handoff/final_handoff_tasks.csv` as the short operational checklist once the archive is restored on a network-enabled machine.
