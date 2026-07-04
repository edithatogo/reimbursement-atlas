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

