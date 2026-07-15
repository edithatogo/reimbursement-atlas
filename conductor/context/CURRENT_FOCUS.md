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

The current focus is evidence-grade transition and release handoff. Workflow policy, automation-control, action SHA-pinning, SBOM, CodeQL, secret-history and zizmor gates are green. The next work is to validate reviewed live-source bundles, complete accountable licence/domain/methods review, and preserve consumer-side attestation verification without weakening publication gates.


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
## v17 focus update

The current focus is now evidence-grade transition: run the hardened source-download plan in a network-enabled environment, then use the evidence-readiness matrix to decide which research question can move from `prototype_ready` to `evidence_ready`. Source/schema drift and data dictionary outputs must be regenerated before any Hugging Face, OSF, Zenodo or GitHub release artefact is published.


## v18 focus update

The repo is ready for local download and continuation. v18 adds source-specific contract checks, GitHub Project import rows and a final handoff checklist. The final handoff table is the authoritative list of remaining tasks that require a network-enabled checkout, repository secrets or human licence/research review.

Immediate implementation focus:

1. Run `source-download-plan` and generated curl commands on a network-enabled local machine.
2. Rerun `source-validation` and `source-contracts` before any reviewed-source bundle is parsed.
3. Import `.github/generated-issues` and `data/derived/github_project/github_project_items.csv` into GitHub Issues/Projects once credentials exist.
4. Use `data/derived/final_handoff/final_handoff_tasks.csv` to execute the remaining network/credential/review-dependent work.
5. Regenerate release-readiness after the source, security, OSF and Hugging Face gates complete.

## v19 follow-up

Local quality, source-contract validation and release readiness are now green. The live
MBS reviewed bundle is staged, and the source-contract rules now skip landing-page and
manual-review records explicitly instead of treating them as missing. Next useful work is
the remaining live-source acquisitions plus any parser or validator refinements that real
downloads expose. A current-channel stack canary is now the place to watch Python 3.14
patches, dashboard dependency drift and Mojo toolchain refreshes before they reach the
main release path.

## 2026-07-11 security, harness and OSF convergence

Action references are SHA-pinned, `zizmor` medium findings are blocking, strict branch protection requires 20 quality/security/harness checks, and full-history secret scanning plus reproducible-build verification pass. The continuous-security and harness-engineering tracks are complete. CI/CD remains open only for consumer-side attestation verification and continuing canary maintenance.

`osf-cli-go` is pinned at stable `v1.0.0` for automation and verified through Go module provenance. OSF sync manifests are checksum-bearing and fail closed. Remote OSF mutation, registration and public release remain blocked by human methods, domain, licence and governance review and by the absence of manifest-native remote path reconciliation.

Immediate focus:

1. Validate ignored live-source files and produce licence-reviewed derived-only bundles.
2. Complete CMS CLFS/CPT derived-field licence review and mapping adjudication.
3. Maintain consumer-side attestation verification for every tagged release.
4. Complete OSF credential-provider, idempotent sync and registration-drift issues without weakening human approval gates.
5. Promote analyses from pipeline prototypes only after reviewed sources and signed protocols exist.

## 2026-07-15 public product and citation maturity

The next implementation phase is public-product readiness. The new
`track_public_product_citation_dashboard` is the parent planning surface for citation
metadata, current-state documentation, dashboard deployment, accessible exploration,
provenance drill-down, machine-readable status and archival DOI release.

Its generated child issue drafts include an explicit parent-issue reference so Conductor,
the GitHub Project export and future native GitHub sub-issues remain cross-referenced.

## 2026-07-15 operational hardening and public dashboard deployment

The generated source-download launcher now delegates to the managed `uv` acquisition
path, ensuring shell-launched downloads write the same attempt records and metadata
sidecars as the CLI. The path was reviewed and corrected for the launcher’s three-level
location under `data/derived/source_downloads/`; the end-to-end launcher run recorded
three downloaded and six licence-gated attempts without tracking raw payloads.

PR #154 merged this fix as `7fb9377`. GitHub Pages is enabled and the dashboard is live
at `https://edithatogo.github.io/reimbursement-atlas/`; its deployment workflow and
browser smoke gate passed. Dependabot security updates and private vulnerability
reporting are enabled. The nonsecret Hugging Face target variables are configured,
while `HF_TOKEN` and OSF project configuration remain intentionally token/review gated.

The current public product is software-release ready, but evidence publication and
policy claims remain fail-closed until licence review, human mapping/research review,
OSF registration and Hugging Face publication gates are satisfied.
Historical MBS/PBS coverage remains owned by `track_live_source_ingestion`; release DOI
work remains owned by `track_data_packaging_standards`; documentation freshness remains
owned by `track_ci_cd_supply_chain`.
The historical MBS metadata inventory is now implemented: 343 official targets across 32
archive pages are tracked under `data/seed/historical_mbs_archive_targets.jsonl` and
`data/derived/historical_sources/`. The targets remain manual/licence-review only; this
inventory does not authorize raw acquisition or redistribution.

## 2026-07-15 continuation: publication controls and reproducible evidence

HF publication infrastructure is now configured with repository secret `HF_TOKEN` and
the dataset/Space variables. The dry-run workflow passed on GitHub Actions without
mutating either remote. PR #157 added a fail-closed publication gate, and PR #158
refreshed generated evidence from a clean checkout so ignored `data/raw_live/` files
cannot change committed validation outputs. The latest merged commit is `6550e64`.

At that point in the continuation history, the remaining blockers were external and
intentionally explicit: `OSF_PROJECT_ID` was not configured, local OSF authentication
was unavailable, source and derived artefacts still needed human licence review, mapping
calibration and methods review remained outstanding, and two current MBS source contracts
required the ignored raw payloads for clean-checkout reconciliation. The public
dashboard remains software-release ready but not evidence- or policy-release ready.

The historical landing-page contract correction is now merged as `3c2d46f`: live MBS
validation reports two current payloads as `pass` and all seven metadata/manual-review
records as `skipped`; clean CI continues to report only the two current raw MBS files as
missing because raw caches are intentionally absent there.

## 2026-07-15 OSF private infrastructure provisioned

PR #163 merged as `a7d2926` and added an idempotent, token-gated `provision=true` mode
to the OSF workflow. Run `29419950570` created the private OSF project `q8cnx` titled
`Reimbursement Atlas`; the sanitized artifact was verified and the repository variable
`OSF_PROJECT_ID` was configured. This does not constitute registration or publication:
the OSF sync manifest remains fail-closed until protocol, licence, domain and human
research review gates are explicitly approved.

The final-handoff generator now classifies HF and OSF work as review-blocked rather than
secret-blocked because both credentialed dry-run paths are configured and verified.

## 2026-07-16 continuation — merged public-product release state

The reviewed MBS TXT-pair provenance work is merged on `main` at `38a3990`. The July 2026
item-map and descriptor pair produced 14,856 derived schedule rows, remains raw-cache-only
for source payloads, and is still pending human Commonwealth/licence and domain review.
Publication manifests, the data dictionary and research package now enumerate nested reviewed
bundle files without exposing local paths or raw payloads.

Repository-controlled recommendations are implemented and monitored: GitHub Pages is live,
source-health/source-drift and stack-canary workflows are scheduled, citation and machine-
readable status contracts are validated, HF/OSF workflows are token-gated and fail closed,
Zenodo metadata is prepared without deposition, and release attestations have consumer
verification guidance.

The active queue is now explicitly external or human-reviewed:

1. Review the MBS bundle and CMS CLFS/PFS/ASP reuse boundaries (`#23`, `#24`, `#26`, `#27`).
2. Acquire and review a PBS monthly extract (`#25`) and approve historical MBS/PBS scope.
3. Adjudicate mapping controls and approve a research-specific threshold (`#10`, `#11`).
4. Approve and register the OSF protocol package (`#134`, `#135`, `#109`–`#113`).
5. Approve HF dataset/Space publication (`#114`, `#115`) and later Zenodo DOI deposition (`#121`).
6. Complete cross-platform dashboard visual review; Chromium smoke and build gates already pass.

The PBS acquisition path is now explicitly documented: the official API catalogue identifies the
active v3 server, OpenAPI export, `/schedules`, `/items` and `/fees` operations, and JSON/CSV
responses; the data route requires an external subscription key. The documentation page is not
the monthly extract.
Plan-only source regeneration preserves prior attempt evidence; it no longer erases the live MBS
download history.

Do not convert any of these states to evidence-ready, policy-ready or publicly published
without the corresponding human decision recorded in `docs/REVIEW_DECISIONS.md`.
