# Conductor implementation tracks
These tracks are generated/maintained alongside `data/seed/conductor_tracks.*` and `data/seed/roadmap_functions.*`. They are also reflected in `.github/generated-issues/`.

## [~] track_runtime_mojo_python314: Mojo-first runtime and Python 3.14 compatibility

Priority: **must**
Phase: `hardening`
Workstream: `runtime`

Goal: Make Mojo the explicit performance-kernel layer while targeting Python 3.14 for orchestration and packaging once CI can install it.

Deliverables:
- Mojo kernel smoke tests
- Python 3.14 CI matrix
- runtime target table
- fallback policy for current sandbox

Tracked functions/issues:
- `func_mojo_tokenizer` — Implement Mojo fixed-width tokenizer kernel and Python parity test (prototype, mojo_kernel)
- `func_mojo_fuzzy_prefilter` — Prototype Mojo fuzzy prefilter for large crosswalk candidate sets (prototype, mojo_kernel)
- `func_python314_ci` — Add Python 3.14 CI matrix and keep sandbox fallback documented (implemented, github_action)

## [~] track_live_source_ingestion: Evidence-grade live source ingestion

Priority: **must**  
Phase: `implementation`  
Workstream: `data`

Goal: Download or API-fetch public sources using curl/wget/API clients, snapshot them locally, and publish derived-only validated records.

Deliverables:
- source downloader
- download attempt log
- MBS pair bundle
- CMS CLFS safe parser
- PBS API extract

Tracked functions/issues:
- `func_source_download` — Implement robust source download command with curl/wget/API fallbacks (implemented, cli)
- `func_source_snapshot` — Maintain source snapshot provenance for all reviewed downloads (implemented, cli)
- `func_source_diff` — Add source drift and schema diff reports (implemented, data_pipeline)
- `func_source_download_hardened` — Harden source download commands with quoting, retry, resume and sidecar metadata (implemented, cli)
- `func_historical_mbs_pbs_bundles` — Expand reviewed coverage with historical MBS and PBS bundles (planned, data_pipeline)

## [~] track_research_protocols_osf: OSF research protocol and report workflow

Priority: **must**  
Phase: `design`  
Workstream: `research`

Goal: Treat each policy question as a protocolled research output with OSF components, reports, appendices and preprint pathways.

Deliverables:
- OSF component plan
- protocol templates
- research question reports
- preprint checklist

Tracked functions/issues:
- `func_osf_protocol_export` — Generate OSF protocol pack from research question registry (implemented, data_pipeline)
- `func_osf_api_publish` — Add token-gated OSF API publication workflow (implemented, github_action)

## [x] track_publication_hf_spaces: Hugging Face dataset and Spaces publication

Priority: **must**  
Phase: `implementation`  
Workstream: `publication`

Goal: Package licence-safe derived data for Hugging Face Datasets and deploy the static dashboard to Hugging Face Spaces.

Deliverables:
- dataset card
- Space README
- conditional publish workflow
- static dashboard bundle

Tracked functions/issues:
- `func_hf_dataset_publish` — Implement conditional Hugging Face dataset publication workflow (implemented, github_action)
- `func_hf_space_deploy` — Implement conditional Hugging Face Space deployment workflow (implemented, github_action)

## [~] track_data_packaging_standards: Research-data packaging standards

Priority: **should**  
Phase: `implementation`  
Workstream: `publication`

Goal: Emit Frictionless Data Package, RO-Crate, DCAT and citation metadata for release candidates.

Deliverables:
- datapackage.json
- ro-crate-metadata.json
- DCAT JSON-LD
- Zenodo metadata

Tracked functions/issues:
- `func_frictionless_package` — Add Frictionless Data Package generator (implemented, data_pipeline)
- `func_ro_crate` — Add RO-Crate metadata generator (implemented, data_pipeline)
- `func_dcat` — Add DCAT JSON-LD export (implemented, data_pipeline)
- `func_data_dictionary` — Generate public artefact data dictionary (implemented, data_pipeline)
- `func_zenodo_doi_release` — Create signed release and Zenodo DOI after publication approval (planned, github_action)

## [~] track_mapping_workbench: Human-in-the-loop mapping workbench

Priority: **must**  
Phase: `implementation`  
Workstream: `mappings`

Goal: Move from deterministic candidate crosswalks to adjudicated mapping evidence with gold standards, negative controls and reviewer state.

Deliverables:
- review UI tables
- gold-standard fixtures
- negative controls
- mapping confidence calibration

Tracked functions/issues:
- `func_mapping_review_ui` — Build dashboard mapping adjudication views (prototype, dashboard)
- `func_gold_standard_mappings` — Add mapping gold-standard and negative-control datasets (planned, data_pipeline)

## [~] track_ci_cd_supply_chain: CI/CD and supply-chain hardening

Priority: **must**
Phase: `hardening`
Workstream: `automation`

Goal: Make release gates enforceable through GitHub Actions, action SHA pinning, SBOMs, attestations, Scorecard, CodeQL, dependency review and zizmór.

Deliverables:
- SHA-pinned actions
- blocking workflow security
- pip-audit network CI
- branch protection as code

Tracked functions/issues:
- `func_action_sha_pin_bot` — Automate GitHub Action SHA pinning (prototype, github_action)
- `func_release_attestation_verify` — Add consumer-side artifact attestation verification (prototype, github_action)
- `func_docs_freshness_gate` — Add documentation freshness and claim-validation gate (planned, github_action)

## [ ] track_policy_demonstrators: First policy demonstrators

Priority: **must**  
Phase: `analysis`  
Workstream: `analytics`

Goal: Produce publishable demonstrations for genomics/pathology, cognitive-procedural relativities, medicine price opacity and coverage discretion.

Deliverables:
- protocolled analyses
- reproducible notebooks/scripts
- policy briefs
- dashboard views

Tracked functions/issues:
- `func_genomics_demo` — Implement genomics/pathology policy demonstrator (planned, data_pipeline)
- `func_cognitive_procedural_index` — Implement cognitive versus procedural relativity analysis (planned, data_pipeline)
- `func_medicine_opacity_index` — Implement medicine price-opacity scorecard (planned, data_pipeline)


## [x] track_data_quality_evidence: Data quality, source validation and evidence readiness

This track makes source-content validation, data-quality checks and research-question linkage matrices first-class release gates. It ensures live downloaded files are validated locally, seed and derived tables pass table-level expectations, and every research question can be traced to sources, mappings and output artefacts before OSF/Hugging Face publication.
## v17 added gates

- Evidence-readiness matrix: one generated row per protocolled research question, combining protocol completeness, data-quality blockers, source-validation blockers, dataset/mapping/output linkages and recommended next action.
- Source/schema drift: generated parity checks for CSV/JSONL mirrors now, and the same interface for future source-version comparisons after live ingestion.
- Public artefact data dictionary: generated column and row-count metadata for publication-manifest candidates, intended for Hugging Face dataset cards, OSF appendices and release review.


## v18 additions

- **Source contracts:** source-specific validation between generic download checks and parser execution.
- **GitHub Project export:** generated project rows for tracks, issue drafts, priorities, milestones and views.
- **Final handoff:** environment-dependent tasks with exact commands and unblock conditions.

## [x] track_continuous_security_assurance: Continuous security assurance and branch enforcement

Priority: **must**
Phase: `hardening`
Workstream: `security`

Deliverables:
- blocking actionlint and zizmor checks
- full-history secret scanning
- reproducible package-build verification
- required protected-branch security contexts

## [x] track_harness_engineering: Layered harness engineering and deterministic regeneration

Priority: **must**
Phase: `hardening`
Workstream: `quality`

Deliverables:
- bounded property, integration and end-to-end test matrix
- deterministic generated-output verification
- bounded mutation testing
- retained harness evidence and failure diagnostics

## [~] track_public_product_citation_dashboard: Public product, citation and dashboard maturity

Priority: **must**
Phase: `implementation`
Workstream: `dashboard`

Goal: Present the atlas as a current, citable and accessible public product with a deployed dashboard, trustworthy status reporting and release-grade scholarly metadata.

Dependencies: `track_live_source_ingestion`, `track_publication_hf_spaces`, `track_data_packaging_standards`, `track_data_quality_evidence`, `track_ci_cd_supply_chain`

Context: [specification](tracks/track_public_product_citation_dashboard/spec.md) | [implementation plan](tracks/track_public_product_citation_dashboard/plan.md)

Parent GitHub issue: `Public product, citation and dashboard maturity`

Tracked sub-issues:
- Correct and schema-validate `CITATION.cff`
- Rewrite README for current product state and citation guidance
- Deploy the static dashboard to GitHub Pages and mirror to Hugging Face Spaces
- Build an executive dashboard overview with readiness and blocker KPIs
- Add dashboard search filters downloads and stable deep links
- Add dashboard provenance and mapping-evidence drill-down
- Add dashboard accessibility performance and visual regression gates
- Publish machine-readable project status and readiness badges
- Add documentation freshness and claim-validation gate
- Create signed release and Zenodo DOI after publication approval
- Expand reviewed coverage with historical MBS and PBS bundles
