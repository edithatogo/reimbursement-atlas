# Current focus

The repo is now in the reviewed-source preparation and mapping-workbench phase. v10 adds a redacted reviewed-source metadata rule and a dedicated MBS TXT-pair bundle workflow.

## Immediate focus

1. Keep all public artefacts dashboard-safe and licence-safe.
2. Validate manually downloaded live sources only through `data/raw_live/` plus snapshot metadata and derived-only outputs.
3. Use the manual acquisition pack to guide the first real MBS July 2026 TXT-pair bundle parse.
4. Treat mapping evidence and vector search outputs as review queues, not equivalence statements.
5. Keep CLI/API/MCP surfaces read-only until acquisition and licence controls are mature.
6. Keep quality gates green: Ruff, basedpyright, Bandit, compileall, uv build, >90% coverage, npm audit and Astro build.
7. Record optional toolchain status honestly; Mojo is available via uv tool, while official Pixi may be blocked by container DNS or missing.

## Current generated artefacts

- `data/seed/source_readiness.*`
- `data/seed/analysis_readiness.*`
- `data/seed/first_wave_ingestion_plan.*`
- `data/seed/source_status.*`
- `data/seed/source_files.*`
- `data/derived/vertical_slice/*`
- `data/derived/vertical_slice/mapping_evidence_matrix.*`
- `data/derived/manual_acquisition_pack/*`
- `data/derived/vector_seed/schedule_item_vectors.*`
- `data/derived/publication_manifest.json`
- `data/derived/optional_toolchain_installs.*`
- `apps/dashboard/public/data/*`

## v10 artefacts

- `docs/MBS_REVIEWED_PAIR_BUNDLE.md`
- `docs/ADRs/0021-redacted-reviewed-source-bundles-and-mbs-pairing.md`
- `conductor/sessions/2026-07-04-v10-mbs-pair-bundles.md`

## v9 artefacts

- `docs/MANUAL_ACQUISITION_PACK.md`
- `docs/MAPPING_WORKBENCH.md`
- `docs/OPTIONAL_TOOLCHAIN_INSTALLS.md`
- `docs/ADRs/0019-official-toolchain-gates-and-wrong-tool-detection.md`
- `docs/ADRs/0020-deterministic-vector-mapping-before-embeddings.md`
- `conductor/sessions/2026-07-04-v9-toolchain-and-mapping-workbench.md`

## Next agent handoff

Start with `docs/MANUAL_ACQUISITION_PACK.md`, `docs/MAPPING_WORKBENCH.md`, `docs/OPTIONAL_TOOLCHAIN_INSTALLS.md`, `docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md`, `docs/MBS_TXT_PAIR_PARSER.md`, and `conductor/sessions/2026-07-04-v9-toolchain-and-mapping-workbench.md`.

Immediate next step: manually download the July 2026 MBS item-map and descriptor TXT files, place them in `data/raw_live/au_mbs/`, run `reviewed-mbs-txt-pair-bundle`, and commit only derived rows/provenance after reviewing licence and validation warnings.

## 2026-07-04 v11 current focus

The current focus is CI/CD and supply-chain hardening before first live-source ingestion. The repo now emits workflow policy, automation-control, action SHA-pinning and SBOM artefacts. The next network-enabled step is to resolve all tag-pinned GitHub Actions references in `data/derived/repo_automation/action_sha_pin_plan.csv` to full commit SHAs, then make zizmor blocking instead of advisory.


## 2026-07-04 v13 current focus

The current focus is now release-readiness convergence. Local Python, Node, dashboard, SBOM, public-data and architecture gates are machine-readable. Remaining work is mostly external: run `pip-audit --strict` in network-enabled CI, validate official Pixi in a normal environment, resolve GitHub Action refs to immutable SHAs, then make `zizmor` blocking.

New artefacts:

- `data/derived/architecture/*`
- `data/derived/release_readiness/*`
- `docs/ARCHITECTURE_BOUNDARIES.md`
- `docs/RELEASE_READINESS.md`
- `docs/ADRs/0024-architecture-boundaries-as-generated-quality-gate.md`
- `docs/ADRs/0025-release-readiness-matrix.md`
- `conductor/sessions/2026-07-04-v13-architecture-release-readiness.md`

## v14 focus — roadmap-to-issues, OSF/HF publication, Mojo/Python 3.14 and executable acquisition

The current focus is to convert recommendations into machine-readable Conductor tracks, GitHub issue drafts and publication artefact plans. The v14 pass adds tracks for evidence-grade ingestion, Mojo-first runtime development, Python 3.14 CI, OSF protocols/reports, Hugging Face dataset/Space publication, research packaging, mapping review and CI/CD hardening.

Immediate implementation focus:

1. Run real-source acquisition in a network-enabled environment using `source-download-plan --attempt` and the reviewed-source bundle commands.
2. Keep raw files under ignored `data/raw_live/` paths; commit only derived, licence-reviewed outputs.
3. Promote the generated issue drafts to GitHub Issues/Projects once the remote repository exists.
4. Use OSF components for protocols, research-question reports, preregistration materials and future preprint/paper artefacts.
5. Use Hugging Face for permissive derived datasets and the Astro dashboard Space.
6. Keep Mojo kernels for performance-critical parsing/prefiltering and Python 3.14 for orchestration/interfaces until Mojo library coverage is sufficient.

## v15 focus — hardened acquisition and protocol gates

The current focus is now first real-source ingestion with stronger guardrails. v15 hardened generated source-download commands and added an OSF-aligned protocol-status gate.

Immediate implementation focus:

1. Run `data/derived/source_downloads/download_commands.sh` in a network-enabled environment.
2. Keep raw downloads in ignored `data/raw_live/` storage and use reviewed-source bundle commands for derived outputs.
3. Add source-specific validators for real MBS, CMS CLFS and PBS files after first downloads succeed.
4. Use `data/derived/protocols/protocol_status.csv` to complete protocol sections before OSF upload/preregistration.
5. Keep generated issue drafts in sync so every track, dataset, protocol, validator and output has a GitHub Project work item.

## v16 focus — source validation, data-quality gates and research linkages

The current focus is evidence readiness after acquisition hardening. v16 adds post-download source-content validation, table-level data-quality checks and a research-question linkage matrix.

Immediate implementation focus:

1. Run source downloads in a network-enabled environment, then rerun `source-validation` before parsing.
2. Treat `data/derived/data_quality/summary.json` as a release gate; blocking failures must be zero before publication.
3. Use `data/derived/roadmap_linkages/research_dataset_linkages.csv` to ensure every research question has sources, mapping resources and outputs before OSF preregistration or report work.
4. Add source-specific schema/record-count validators after the first real MBS, CMS CLFS and PBS downloads succeed.
5. Keep GitHub issue drafts regenerated from Conductor so these gates appear in GitHub Projects.
