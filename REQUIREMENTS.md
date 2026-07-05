# Requirements using MoSCoW

## Vision

Build a bleeding-edge, reproducible comparative reimbursement atlas that maps public billing schedules, coverage decisions, drug reimbursement lists, hospital tariffs, genomic test directories and relevant ontologies into a policy-analysis platform.

## Must have

### Product and research requirements

- Maintain a source registry covering CMS, Australian MBS/PBS, IHACPA, NHS England, Canadian provinces and selected OECD/Asian comparators.
- Maintain an analysis catalogue focused on policy-relevant questions, not just raw price comparison.
- Distinguish schedule fees, benefits, tariffs, allowed amounts, list prices, payment points, subsidies, patient co-payments and effective net prices.
- Capture evidence/coverage decision pathways for MSAC, PBAC, CMS NCD/LCD, NHS genomic test directory and selected HTA bodies.
- Support reproducible data provenance: source URL, publication date, retrieval date, format, licence notes, checksum, parser version.
- Implement typed source, analysis and ontology registries using Pydantic v2.
- Use Polars, Arrow and DuckDB as the analytical spine.
- Include LanceDB design for semantic retrieval over source documents, restrictions and coverage text.
- Include graph export files for Cosmograph.
- Establish Conductor context management so future agents can load current project intent, constraints, decisions and open questions.

### Engineering requirements

- Use `pyproject.toml`, `uv_build` and Pixi.
- Use Ruff with strict all-rule selection, preview enabled, and explicit ignores.
- Use basedpyright in strict mode.
- Target Python 3.13+.
- Include tests across unit, property, integration, end-to-end and smoke layers.
- Enforce target coverage above 90%.
- Include mutation testing with mutmut and property testing with Hypothesis.
- Include security automation: CodeQL, dependency review, pip-audit, Bandit, secret scanning guidance, Dependabot and Renovate.
- Include GitHub issue templates, pull-request template, labels and project-planning scaffold.
- Include dashboard scaffold using Astro 7 and Cosmograph.

### Data governance requirements

- Do not commit restricted ontology source dumps, CPT descriptors, DSM-5 text, UMLS source files, confidential PBS deed data, proprietary tariff extracts or scraped content that cannot be redistributed.
- Separate permissive seed data from user-supplied/licensed local data.
- Build licence gates before Hugging Face dataset upload.
- Preserve source versioning and retrieval metadata for all schedule imports.
- Keep live raw source downloads in ignored local cache paths until explicit redistribution review.
- Enforce a public-data policy check that prevents raw/local cache files from being committed.

## Should have

- First-wave source ingestion adapters for MBS XML, PBS CSV/API, CMS PFS, CMS CLFS, CMS ASP and NHS genomic directory files.
- A source-quality scoring framework: machine readability, historical depth, utilisation linkage, licence clarity, effective-price opacity and comparability.
- A mapping workbench for service concepts, drug concepts, genomic tests, indications, DRGs/APCs and restrictions.
- DuckDB analytical marts for source registry, schedule item snapshots, restrictions, concept mappings and analysis outputs.
- LanceDB vector tables for coverage text, item descriptors, restrictions and decision documents.
- Ontology interfaces for LOINC, RxNorm/RxNav, ICD-11, ATC, HPO, HGNC, SNOMED CT where licensed, and UMLS where user-supplied.
- A GitHub Projects automation script mapping Conductor roadmap epics into issues.
- A Hugging Face dataset card and upload workflow for permissive seed data.
- A Hugging Face Space dashboard deployment workflow.

## Could have

- Mojo kernels for parsing, embedding pre-processing, fuzzy matching or graph edge construction.
- CLI commands for source validation, local file snapshotting, local-source parsing, scoring, graph export, ingestion, mapping, analysis and dashboard export.
- MCP server exposing registry search, source provenance, schedule lookup and analysis runs.
- FastAPI service for internal dashboards or external API use.
- dbt-style transformations or SQLMesh integration for analytical mart governance.
- Great Expectations, Narwhals, Ibis or DataFusion exploration if they simplify quality checks or portability.
- Evidence retrieval integration with Elicit, Consensus or PubMed for coverage-decision evidence trails.
- OpenTelemetry traces for ingestion jobs.
- SBOM generation and SLSA provenance for releases.

## Won't have yet

- Patient-level claims analytics.
- Confidential effective net drug prices.
- Full CPT descriptor redistribution.
- UMLS, DSM-5 or proprietary ontology mirroring.
- Automated one-to-one mapping between MBS and CPT/HCPCS without human review.
- Production API, MCP server or hosted dashboard until the design layer, source registry, licence gates and first vertical slice mature.
- Any claim that cross-country prices are directly comparable without bundle, population, exchange-rate and purchasing-power caveats.

## Success criteria for design maturity

- At least 60 source families are registered and scored.
- At least 25 policy-relevant analyses are specified.
- Licence status is explicit for every source and ontology.
- First-wave ingestion backlog is issue-ready.
- Architecture diagrams and ADRs are accepted.
- Seed data validates locally and in CI.
- Dashboard can render seed graph without live ingestion.
- There is a clear path from source registry to GitHub issues to Hugging Face dataset/Space deployment.

## v5 requirements: reviewed-source and publication readiness

| Priority | Requirement | Status |
|---|---|---|
| Must | Provide a reviewed-source bundle command that snapshots, parses and reports on one manually downloaded source file without copying raw data. | Implemented |
| Must | Validate JSONL/CSV seed-table synchronisation before dashboard or dataset publication. | Implemented |
| Must | Generate a candidate publication manifest with row counts, byte sizes and SHA-256 checksums. | Implemented |
| Must | Keep restricted ontology dumps, CPT/DSM/UMLS text and confidential prices out of committed artefacts. | Implemented as policy and tests; requires human review for live data |
| Should | Add machine-readable analysis recipes tied to analysis catalogue records and quality gates. | Implemented |
| Should | Add local-only ontology concept seeds for LOINC/HPO/ATC/RxNorm-style mapping workflow testing. | Implemented with synthetic fixtures |
| Could | Add dashboard pages for publication-manifest and analysis-recipe status. | Planned |
| Won't now | Automate network fetching of live public files. | Deferred until licence/provenance gates are reviewed |

## v6 requirements: installed toolchain and enforceable quality gates

| Priority | Requirement | Status |
|---|---|---|
| Must | Install and exercise the Python dev stack locally with `uv`. | Implemented |
| Must | Pass Ruff lint and format checks over source, scripts and tests. | Implemented |
| Must | Pass basedpyright strict type checking over source and scripts. | Implemented |
| Must | Enforce >90% coverage over the core library. | Implemented |
| Must | Replace unsafe XML parsing with `defusedxml`. | Implemented |
| Must | Build source and wheel distributions with `uv build`. | Implemented |
| Should | Convert the unresolved `test-goblin` placeholder into a practical adversarial-testing extra. | Implemented with Hypothesis, mutmut and pytest-randomly |
| Should | Add documentation for local QA, coverage policy and test-goblin compatibility. | Implemented |
| Could | Run full mutation testing and Scalene profiling on every commit. | Deferred to nightly/long-running CI |
| Won't now | Treat optional API, MCP, dashboard and warehouse scaffolds as production surfaces. | Deferred |

## v8 requirements refinement

### Must

- Maintain exact `SourceFileRecord` metadata for every live-source file, landing page, endpoint, or licence gate before parser promotion.
- Keep CMS/AMA-gated CLFS downloads manual-only and prevent CPT descriptor redistribution.
- Record external quality gates as `passed`, `failed`, `blocked_network`, `missing_tool`, or `timed_out`.

### Should

- Validate the MBS TXT pair parser against the real `20260701_MBSONLINE_IMAP.TXT` and `20260701_MBSONLINE_DESC.TXT` files in an ignored local cache.
- Surface source-file and external-gate status in the dashboard and Conductor handoff.

### Could

- Add pair/multi-file reviewed-source bundle support for MBS item-map plus descriptor files.
- Add an OSV or GitHub Advisory fallback when `pip-audit` cannot reach PyPI.

## v15 requirements refinement

### Must

- Source acquisition commands must be shell-quoted, retryable, resumable and licence-gated.
- Protocol/report completeness must be generated before OSF publication is treated as ready.
- GitHub issue drafts must include source-validation, checksum-pinning and protocol-review tasks.

### Should

- Source-specific validators should be added after the first real MBS, CMS and PBS files are downloaded.
- Protocol templates should gain method-specific sensitivity-analysis and bias-assessment sections before the first publishable paper.
