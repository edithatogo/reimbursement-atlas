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

## 2026-07-16 source acquisition refresh

The hardened acquisition workflow was rerun against all nine configured source records.
The July 2026 MBS item-map and descriptor TXT pair downloaded successfully into ignored
local raw storage and revalidated against the reviewed derived bundle. PBS remains blocked
by the absent `PBS_API_SUBSCRIPTION_KEY`; historical MBS and CMS records remain explicit
licence-gated or landing-page/manual-review targets. No raw payloads are tracked.

The scheduled source-health workflow now also runs the hardened acquisition attempt with the
PBS key injected only from GitHub Actions secrets. Raw files remain ephemeral runner state;
only redacted acquisition, validation, contract, drift and readiness evidence is uploaded.

The source-health, final-handoff, data-quality, dashboard seed, local-quality and external
quality-gate outputs were regenerated. Repository release readiness remains green, while
research publication, OSF registration, evidence release and policy claims remain fail-closed.

The local dashboard browser smoke suite was rerun after the source-health automation merge:
18 desktop/mobile Chromium route tests passed and `npm audit` reported zero vulnerabilities.
This is automated smoke evidence only; cross-browser/OS visual baseline and accessibility
approval remains a human review item.

## 2026-07-16 deterministic release manifest

The tagged release workflow now generates a relative-path, checksum-bearing
`release-manifest.json` binding distributions, the source archive and SBOMs to the release tag
and commit. GitHub attests and verifies the manifest before publishing it. This strengthens
consumer software provenance without changing the fail-closed status of Zenodo, OSF, Hugging Face,
source licensing, evidence or policy-claim gates.

The release consumer path now also has an offline verifier for manifest schema, expected tag/commit,
safe relative paths and subject SHA-256 values. Consumers should run it before `gh attestation
verify`; neither check substitutes for the human and publication gates.

## 2026-07-16 live Pages defect follow-up

The public browser check found a deployment-only base-path defect: HTML loaded at the project
site, but root-relative Astro modules returned 404 and prevented hydration. v41 fixes Astro's
Pages base configuration and all dashboard-generated URLs, with a pre-upload artifact gate in
`scripts/check_dashboard_pages_assets.py`. After the protected fix merges, verify the live site
again; visual baseline approval remains a human gate.

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

Native GitHub blocker issues now bind the two remaining release lanes: historical MBS/PBS
coverage is tracked in [#255](https://github.com/edithatogo/reimbursement-atlas/issues/255),
and Zenodo DOI deposition is tracked in
[#256](https://github.com/edithatogo/reimbursement-atlas/issues/256). Both remain fail-closed
until their stated human and external approvals are recorded.

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

## 2026-07-16 dashboard status-card verification

PR #213 merged as `4a64be4`. It separates dashboard readiness values from their descriptions
with explicit block-level elements and adds a homepage browser regression for the layout.
Local browser validation passed all 18 route checks. Pages run `29446529249` passed build,
browser smoke, evidence upload, deployment and live smoke. Its retained artifact
`dashboard-review-evidence-29446529249` contains 18 screenshots and the Playwright report;
the homepage screenshot was inspected and confirms the corrected spacing. Human cross-platform
visual and accessibility sign-off remains an external gate under issue #188.

## 2026-07-16 OSF plan verification

Workflow run `29447241542` on commit `fe4ebc1` passed the pinned OSF plan: protocol-plan
generation, `osf-cli-go` module provenance and unauthenticated CLI contract, fail-closed
synchronization validation, and artifact upload. The downloaded `osf-component-plan` artifact
contained 20 protocol/plan files, no forbidden token or local-path markers, and 15 sync rows
with zero `publish_allowed` rows. OSF registration and publication remain gated on accountable
human methods, domain, licence and governance approval.

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

## 2026-07-16 — PBS multi-endpoint acquisition evidence

The live PBS parser is now paired with a redacted acquisition-evidence validator for the
official v3 `schedules`, `items` and `fees` responses. The July 2026 cache is locally observed
for schedule `4706` with two item pages and one fees response; raw payloads remain ignored.
Tracked evidence records only endpoint metadata, schema/row counts, sizes, checksums and the
`acquired_unreviewed` state. Human field, licence and research review remain required before
derived PBS rows can be published or used for policy claims.

## 2026-07-16 — OSF CLI v1.0 contract hardening

The OSF workflow now pins stable `osf-cli-go v1.0.0` and runs an unauthenticated contract check
for version, export, validation, storage and registration command surfaces. This verifies tool
compatibility without reading tokens or performing network mutation. The OSF manifest, protocol,
licence and human-review gates remain unchanged and fail closed.

## 2026-07-16 — deterministic research packaging

Research-package descriptors now exclude themselves from the publication manifest so repeated
generation is byte-stable. The focused regression test and the three-descriptor checksum
replay gate pass. The generated issue/project rows and roadmap function for this hardening are
tracked under `track_data_packaging_standards`; no publication or licence gate was weakened.

## 2026-07-16 — responsive dashboard smoke

The browser smoke gate now covers all nine public routes in desktop and mobile Chromium profiles,
with CSS-pixel screenshot bounds. The automated matrix passes; cross-platform visual baselines,
accessibility review and all source/publication decisions remain human handoff gates.

## 2026-07-16: Dashboard keyboard interaction smoke

The Playwright browser suite now verifies that the first public table search control is keyboard
focusable and filters rows, in addition to the existing axe-core, route, performance and
screenshot checks. This improves automated interaction evidence without converting it into human
WCAG or cross-platform approval.

## 2026-07-16 — GitHub advanced secret scanning

The live repository has provider secret scanning, push protection and Dependabot security updates
enabled. GitHub's API still reports non-provider secret-pattern scanning and secret-validity checks
as disabled after an idempotent enablement attempt. Issue [#191](https://github.com/edithatogo/reimbursement-atlas/issues/191)
tracks this account-level limitation; no release document claims those controls are active.

## 2026-07-16 — Pixi harness invocation

The Pixi Python test tasks now use `python -m pytest`, avoiding stale console-script shebangs when
an environment has been relocated. Official Pixi unit, smoke, property, integration and end-to-end
lanes pass. Issue [#192](https://github.com/edithatogo/reimbursement-atlas/issues/192) records the
harness hardening change.

## 2026-07-16 — Research-package descriptor refresh

The release-gate hashes were regenerated by the CI-order chain before the committed Frictionless
and RO-Crate descriptors were refreshed. The descriptors are now regenerated against those current
hashes and verified byte-identical across consecutive runs; publication and licence gates remain
unchanged.

## 2026-07-16 — Dashboard accessibility scan

The desktop/mobile Playwright matrix now runs axe-core against all nine public routes. All 18
route/profile checks pass with zero automated violations. Human accessibility sign-off and
cross-platform visual baselines remain explicit release handoff gates under issue [#188](https://github.com/edithatogo/reimbursement-atlas/issues/188).

## 2026-07-16 — Generated-artifact ordering

The research package is now the final generated step after release-readiness and seed-lake in the
repository automation, data-smoke and deterministic-regeneration workflows. This prevents stale
release-gate hashes in Frictionless and RO-Crate descriptors after SBOM or dashboard dependency
changes.

## 2026-07-16 — Secret-scanning scope

Issue [#191](https://github.com/edithatogo/reimbursement-atlas/issues/191) now distinguishes
non-provider pattern coverage from partner-pattern validity checks. The user-owned repository has
neither control enabled through the live API; validity checks must not be treated as generic
non-provider coverage.

## 2026-07-16 — Post-deployment Pages smoke

The public dashboard now has an automated post-deployment HTTPS smoke job. Main run `29442862134`
passed build, deployment and live smoke against the canonical project URL, including project-site
prefix, favicon, status manifest, graph CSV and same-origin reference checks. This proves the
deployment contract without changing the separate human visual/accessibility review gate.

## 2026-07-16 — Dashboard review artifact verified

Pages run `29445732834` passed build, browser smoke, deployment and live smoke. Its retained
artifact `dashboard-review-evidence-29445732834` is non-expired and contains the Playwright HTML
report plus 18 desktop/mobile route screenshots and attached performance/axe evidence. Issue [#188](https://github.com/edithatogo/reimbursement-atlas/issues/188)
was updated with the artifact reference; human cross-platform visual and accessibility approval
remains open.

## 2026-07-16 — Token-gated publication dry validation

Main OSF workflow run `29444356493` passed read-only project discovery with the configured token,
the pinned `osf-cli-go` contract and the fail-closed synchronization check. Provisioning and
publication were skipped. Main Hugging Face workflow run `29444461756` passed publication-bundle
validation, dashboard build and candidate-artifact upload with both publication flags disabled;
dataset and Space publication remain gated by licence, evidence and human review.

## 2026-07-16 — Current publication dry-run verification

OSF workflow run `29447241542` on `fe4ebc1` passed the pinned OSF plan, CLI/module provenance,
fail-closed synchronization validation and artifact upload. Its 15 synchronization rows all
remain unapproved. No OSF discovery, provisioning, upload or registration occurred.

Hugging Face workflow run `29447359455` on `fe4ebc1` passed manifest regeneration, dashboard
build, publication-bundle validation and candidate artifact upload. Dataset and Space mutation
jobs were not run. Publication remains closed because research publication, evidence release,
policy claims, protocol readiness and source licence review are incomplete.

## 2026-07-16 — Checksum-bound licence review queue

The publication manifest now has a generated artifact-level review queue under
`data/derived/licence_review/`. It contains 155 checksum-bound candidates, all pending,
with zero approvals and `approval_mutation_allowed: false`. The queue is exposed through
the data dictionary, local quality gates, release readiness, Conductor backlog and generated
GitHub Project artefacts; it improves review readiness without bypassing human licence or
domain decisions.

## 2026-07-16 — Dashboard licence-review surface

The public readiness dashboard now exposes the checksum-bound licence-review queue as a
downloadable, dashboard-safe table. It shows candidate checksums, publication scope, licence
gate and pending status, while explicitly stating that generated rows do not grant approval.
The addition is tracked in generated issue draft #160 and live closed issue [#218](https://github.com/edithatogo/reimbursement-atlas/issues/218), which is on public Project #18.

## 2026-07-16 — Public status blocker transparency

The public status manifest now exposes stable blocker IDs, categories, evidence paths and next
actions for current non-software gates. The dashboard renders these records on the homepage so
software release readiness cannot be mistaken for evidence or publication approval. The work is
tracked in generated issue #161 and live issue [#221](https://github.com/edithatogo/reimbursement-atlas/issues/221), which is on public Project #18.

## 2026-07-16 — Partial source-acquisition status

The final handoff now distinguishes partial acquisition from complete acquisition by matching
download evidence on both source-file ID and target path. The current run is `partial`: the July
2026 MBS pair and PBS documentation were downloaded, but the remaining executable or credential-
gated targets are not represented as complete. This prevents the handoff and release dashboard
from overstating live-source coverage. The change is tracked in generated issue #162 and live
issue [#223](https://github.com/edithatogo/reimbursement-atlas/issues/223), which is on Project 18.

## 2026-07-16 — Public partial-source blocker

The public status manifest and dashboard now consume the final-handoff JSONL directly and expose
`source_acquisition` whenever source ingestion is partial. This keeps the public status surface
consistent with the handoff summary and prevents a partial download run from appearing to have no
source-ingestion action. The change is tracked in the generated issue and Project 18 after
regeneration.

## 2026-07-16 — Source acquisition retry evidence

The hardened acquisition launcher was rerun in the network-enabled environment. It recorded fresh
MBS item-map and descriptor downloads, six intentional licence-gated skips, and an explicit
`blocked_secret` PBS schedules attempt because `PBS_API_SUBSCRIPTION_KEY` is absent. Source
validation and source contracts pass, but the final handoff remains `partial`; the new attempt
history does not change evidence or publication readiness.

## 2026-07-16 — Automation documentation drift audit

The GitHub automation documentation was corrected to describe SBOM generation and artifact
attestation as implemented controls, with the consumer verification guide as the operational
entry point. The live account limitation for non-provider secret-pattern scanning remains a
separate, accurately documented external hardening item.

## 2026-07-16 — OSF non-mutating workflow verification

OSF workflow run `29453951281` passed on the current `main` tip with `publish=false`,
`discover=false` and `provision=false`. The pinned `osf-cli-go v1.0.0` module provenance and
unauthenticated CLI contract passed, and the checksum-bound sync manifest remained fail-closed.
No OSF project, registration or file mutation was attempted.

## 2026-07-16 — Hugging Face non-mutating workflow verification

Hugging Face workflow run `29454414526` passed on the current `main` tip with
`publish_dataset=false` and `publish_space=false`. Publication manifests regenerated, the
dashboard build passed and the candidate bundle validator passed; both remote publication jobs
were skipped. No dataset or Space mutation was attempted.

## 2026-07-16 — OSF reconciliation input hardening

The repository-owned OSF reconciliation boundary now rejects duplicate IDs and paths, path
traversal, absolute local paths, negative sizes and malformed SHA-256 values before planning any
action. Focused unit and CLI end-to-end coverage passed (`18 passed`); this closes the local
input-safety portion of issue [#134](https://github.com/edithatogo/reimbursement-atlas/issues/134).
Credentialed remote mutation and human publication approval remain intentionally blocked.

## 2026-07-16 — OSF registration snapshot contract

The non-mutating registration drift checker now requires an `osf-registration-snapshot-v1`
schema, an `https://osf.io/` registration URL, a submission timestamp, `immutable: true` and a
lowercase SHA-256 snapshot digest before a remote registration can be considered structurally
valid. Focused OSF/CLI tests passed (`19 passed`); issue [#135](https://github.com/edithatogo/reimbursement-atlas/issues/135)
still requires credentialed export and accountable human approval for any real registration.
## 2026-07-16: Source acquisition health escalation

The scheduled source-health workflow now reports partial, network-blocked and
credential-blocked acquisition as a separate fail-open issue lifecycle. It excludes
licence and human-review blockers, writes `source-health-acquisition-v1` evidence, and
never performs network I/O or raw-cache mutation. See
`conductor/sessions/2026-07-16-v60-source-health-escalation.md`.
## 2026-07-16: Public source-health observability

The public status manifest and dashboard automation view now expose the deterministic
source-acquisition health report. Acquisition follow-up is visible separately from
licence, evidence, research-publication and OSF gates; the dashboard still does not
claim evidence or publication readiness from software readiness.

## 2026-07-16: Secret-name guidance in source-health escalation

Source-health reports now parse only the redacted missing-credential message from acquisition
evidence and expose the required environment-variable name, never a secret value. The current
PBS follow-up therefore identifies `PBS_API_SUBSCRIPTION_KEY` directly while remaining safe for
GitHub issue bodies, public status and dashboard CSV projections.

## 2026-07-16: OSF read-only discovery evidence

OSF workflow run `29459949265` passed with the pinned `osf-cli-go v1.0.0` and read-only
discovery enabled. It confirmed the expected private `Reimbursement Atlas` project `q8cnx`;
provisioning, registration, upload and publication were skipped. The sanitized project listing
is retained only as a seven-day private artifact and is not committed.

## 2026-07-16: OSF idempotent provisioning evidence

OSF workflow run `29460182675` passed with `provision=true` and returned `created: false`,
`id: q8cnx`, `title: Reimbursement Atlas` and `public: false`. The existing private project is
therefore reusable without duplicate creation; no project, component or file was mutated.

## 2026-07-16: Final handoff MBS bundle status correction

The final handoff classifier now reports the July 2026 MBS derived-only review packet as
`complete` when its validation report, summary and redacted schedule records are present,
parse successfully, contain no raw files, and retain the explicit publication-review gate.
This distinguishes completed local bundle generation from the still-pending human licence and
clinical review. The handoff remains `partial` for source acquisition because PBS and other
network/licence-gated targets are not complete.

## 2026-07-16: Dashboard browser-engine coverage

The dashboard browser evidence now covers Chromium desktop/mobile, Firefox desktop and WebKit
desktop in the pinned CI workflow. This improves engine-level regression evidence and retains
30-day test-report artifacts, but does not replace human cross-OS visual, accessibility or
assistive-technology review.

## 2026-07-16: Policy demonstrator linkage surface

The first policy demonstrator now reports genomic schedule-item pricing and genomic coverage
decisions in one typed brief, including the restricted-coverage count and explicit separate
denominators. This remains a fixture-backed, review-gated demonstrator and does not infer
item-level equivalence, causality or evidence-ready policy claims.

## 2026-07-16: Dashboard public deployment verification

The GitHub Pages deployment is now verified at
`https://edithatogo.github.io/reimbursement-atlas/`. Its SHA-pinned workflow builds with the
project-site base path, validates asset prefixes before upload, runs browser smoke coverage,
and performs a post-deploy live HTTP smoke check. The roadmap function is implemented for this
software deployment surface. Hugging Face mirroring, human visual/accessibility review and all
research/publication readiness claims remain separately gated.

The workflow-security path now also runs a fail-closed immutable-action policy gate. All current
external action references are full commit SHAs; local and Docker references remain explicitly
allowed. The resolver remains non-mutating so dependency updates retain human-review provenance.

The dashboard graph now degrades explicitly on Firefox when the Cosmograph device renderer is
unavailable, exposing generated node/edge counts instead of emitting a browser console error.
Chromium and WebKit retain the interactive renderer; the full 40-test local browser matrix passes.

## 2026-07-16: Dashboard provenance and quality

 Dashboard provenance routes and automated experience-quality gates are implemented and review-
gated. Browser automation does not replace human cross-platform visual or assistive-technology
review.

## 2026-07-16: Action-pin maintenance automation

The action-pin maintenance workflow is now implemented. It runs weekly or manually, resolves
all external action refs through the repository resolver, refuses partial updates, preserves
human-readable version comments, and opens a dedicated normal PR rather than mutating `main`.
The immutable-action policy gate remains authoritative, and network/resolution failures remain
fail-closed. See `conductor/sessions/2026-07-16-v77-action-pin-maintenance.md`.

## 2026-07-16: Fuzzy prefilter benchmark evidence

The Python fuzzy-prefilter reference now has a deterministic benchmark over the reviewed
synthetic gold-standard and negative-control fixtures. The current result is recall 1.0,
precision 1.0 and specificity 1.0 at threshold 0.2, but the roadmap function remains a
prototype and the benchmark remains review-required until real-source mappings are adjudicated.
See `conductor/sessions/2026-07-16-v78-fuzzy-prefilter-benchmark.md`.
