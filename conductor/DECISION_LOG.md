# Decision log

| Date | Decision | Status | Notes |
|---|---|---|---|
| 2026-07-03 | Use Conductor as project memory and agent handoff layer. | Accepted | See ADR 0004. |
| 2026-07-03 | Start with design-first repository rather than immediate ingestion. | Accepted | See ADR 0001. |
| 2026-07-03 | Use Polars, Arrow, DuckDB and LanceDB as analytical spine. | Proposed | See ADR 0002. |
| 2026-07-03 | Treat restricted ontologies as local-only user-supplied resources. | Accepted | See ADR 0003. |
| 2026-07-03 | Keep Mojo as performance-extension layer, not first implementation language. | Accepted | Avoid premature optimisation. |
| 2026-07-03 | Target GitHub plus Hugging Face dataset/Space deployment. | Proposed | Requires licence-gated publishing workflow. |

| 2026-07-16 | Process the live July 2026 MBS TXT pair through the redacted reviewed-source bundle workflow. | Accepted | Both source contracts pass; 14,856 derived rows are available for human licence and domain review. Raw files remain ignored and no publication approval is implied. |

| 2026-07-03 | Use reviewed-source bundles before broader live ingestion. | Accepted | See ADR 0011. |
| 2026-07-03 | Require JSONL/CSV seed sync checks and publication manifests. | Accepted | See ADR 0012. |
| 2026-07-03 | Install and enforce the Python quality toolchain locally before further live ingestion. | Accepted | See ADR 0013. |
| 2026-07-03 | Use `defusedxml` for XML-like reimbursement source parsing. | Accepted | See ADR 0014. |
| 2026-07-04 | Commit dashboard package-lock and require `npm ci`/Astro build. | Accepted | See ADR 0015. |
| 2026-07-04 | Keep full mutmut as scheduled/manual gate rather than PR blocker. | Accepted | See ADR 0016. |
| 2026-07-04 | Add exact source-file records before live ingestion. | Accepted | See ADR 0017. |
| 2026-07-04 | Classify external quality gates as passed/failed/blocked/missing rather than pretending network-dependent gates passed. | Accepted | See ADR 0018. |
| 2026-07-04 | Distinguish official optional tools from wrong same-named executables. | Accepted | See ADR 0019. |
| 2026-07-04 | Use deterministic mapping evidence and vector seeds before opaque embeddings. | Accepted | See ADR 0020. |
## 2026-07-04 — Redact reviewed-source bundle paths and pair MBS TXT files

Decision: reviewed-source bundle snapshot exports redact `local_path`, and MBS TXT validation uses a pair-specific bundle command.

Rationale: derived bundles may be shared for review before publication, so they should not leak private raw-cache paths. MBS item-map and descriptor files are separate public source files and need an explicit join contract.

## 2026-07-04 — v11 repo automation, SBOM and provenance gates

Decision: Treat repository automation as a measurable dataset and add generated workflow policy, SBOM and provenance artefacts.

Rationale: The project will publish derived reimbursement datasets; CI/CD posture, release provenance and raw-data publication safeguards must be visible and testable before live-source ingestion expands.

Consequences: v11 adds workflow scanning, action pin classification, OpenSSF Scorecard, zizmor SARIF workflow, release attestations, SBOM summaries and an action SHA-pinning queue. Zizmor remains non-green until tag-pinned actions are migrated to full SHAs in a network-enabled environment.


## 2026-07-04 — v13 architecture boundaries and release readiness

Decision: Treat internal architecture and release readiness as generated, dashboard-visible quality gates.

Rationale: The project now spans parsers, analysis, CLI/API/MCP, dashboard, public-data governance and CI/CD. Static import-boundary checks and a consolidated readiness matrix make drift and external blockers visible before public release.

Consequences: v13 adds `architecture-report` and `release-readiness` commands, CI hooks, dashboard exports, ADRs and release-gate artefacts. Public release remains blocked until network-dependent `pip-audit --strict` can complete and optional hardening warnings are resolved.

## 2026-07-05 — v14 roadmap, OSF/HF, Mojo/Python 3.14 and executable source acquisition

- Added machine-readable Conductor tracks, roadmap functions, dataset candidates, mapping resources, research questions, output artefact plans and runtime targets.
- Expanded generated GitHub issue drafts so roadmap functions, datasets, outputs and research questions can be implemented through GitHub Issues/Projects.
- Targeted Python 3.14 in package metadata, lint/type configuration and Pixi tasks while recording that this sandbox could only validate under Python 3.13.5 because Python 3.14 download resolution was blocked.
- Added a Mojo smoke kernel and Mojo-first runtime documentation for high-throughput parsing and crosswalk prefiltering.
- Added executable curl/wget/API source-download planning and attempt recording. Network/DNS failures are now captured as data-acquisition gate records rather than undocumented manual blockers.
- Added OSF component planning, protocol/report scaffolds and an OSF publication workflow placeholder.
- Added Hugging Face dataset and Space deployment documentation/workflow gates.
- Added Frictionless-style, RO-Crate and DCAT research-package metadata generation.

## 2026-07-05 — v15 hardened source acquisition and protocol-status gates

- Hardened generated `curl`/`wget` commands with retries, resume support, shell quoting, header sidecars and ETag sidecars.
- Kept licence-gated, landing-page and metadata-only records non-executable by default.
- Added protocol-status generation for OSF-aligned research questions, including missing-section checks, word counts, completeness scoring and OSF readiness flags.
- Added documentation, ADRs and dashboard/publication/seed-lake hooks for the new gates.

## 2026-07-05 — v16 source validation, data-quality and research-linkage gates

- Added post-download source-content validation records with redacted local references, checksums, byte sizes, record counts, HTML-error detection and licence-gate skipping.
- Added data-quality checks for row counts, unique ids, referential integrity, required generated artefacts and publication-manifest raw-payload safety.
- Added a research linkage matrix connecting each research question to sources, dataset candidates, mapping resources and output plans.
- Added a Conductor data-quality/evidence-readiness track and corresponding generated GitHub issue coverage.

Decision: no downloaded source file should proceed to parsing/reviewed-source bundles until it has a validation record, and no public release should proceed while data-quality blocking failures are non-zero.
## 2026-07-05 — v17 evidence-readiness, source drift and data dictionary gates

Added generated evidence-readiness rows for each protocolled research question, source/schema drift reporting for paired tabular artefacts, and a public artefact data dictionary. These are now Conductor-visible implementation units and are reflected in generated GitHub issue drafts, dashboard tables, release readiness and publication packaging. Detailed OSF-style protocols and report scaffolds were expanded for all five initial research questions.


## 2026-07-05 — v18 source contracts, GitHub Project export and final handoff

Added source-specific contract validation before reviewed-source parsing, generated GitHub Project import rows from Conductor issue drafts, and created a final handoff checklist for the remaining network/credential/review tasks. These gates are now part of release-readiness, dashboard seed data, publication manifests and the local continuation workflow.

## 2026-07-05 — Codex handoff prompt as a tracked release artefact

Decision: Add a Codex import prompt and internal handoff document so the git bundle can be restored locally and continued by an implementation agent without losing Conductor context.

Rationale: The repo has many generated governance layers. A continuation prompt must explicitly preserve raw-source safety, Mojo/Python 3.14 runtime targets, GitHub issue/project traceability, OSF/Hugging Face gates, and honest blocker reporting.

Consequence: Future bundle exports should include `conductor/handoff/CODEX_IMPORT_PROMPT.md`, and generated GitHub issue/project outputs should include the handoff itself as a tracked workstream.

## 2026-07-11 — Continuous security assurance and layered harnesses

Decision: Promote workflow analysis from advisory to blocking and add separate continuous-security and harness-assurance workflows.

Rationale: SHA-pinned Actions and passing tests are necessary but insufficient. Protected branches need blocking workflow lint/security checks, full-history secret scanning, reproducible-build evidence, bounded layered test harnesses and deterministic regeneration.

Consequences: `zizmor` medium-and-higher findings fail CI, actionlint and Gitleaks run independently, package builds are compared byte-for-byte, and property/integration/E2E/mutation harnesses have explicit timeouts and concurrency cancellation. Publication workflows remain separately environment- and human-gated.

## 2026-07-06 — Hugging Face targets provisioned, OSF remains gated

Live Hugging Face publication targets were provisioned from the repository during Chrome-backed verification:

- dataset `edithatogo/reimbursement-atlas`
- space `edithatogo/reimbursement-atlas`

The Space now has a minimal runnable `app.py` scaffold committed through the official Hugging Face CLI. The automated GitHub Actions publication path remains token-gated, and OSF publication remains blocked until credentials and human review are available.

## 2026-07-15 — Public product track and issue hierarchy

Decision: Add a dedicated public-product Conductor track for citation, README, dashboard
deployment, accessible exploration, provenance, status reporting and archival release.

Rationale: The implementation is materially ahead of its public presentation. These tasks
cross publication, data, security and research concerns, but need one user-facing parent
track with generated child issue references so work remains discoverable without weakening
the existing fail-closed research and licence gates.

Consequences: Generated roadmap-function drafts name the matching parent issue when the
backlog contains it. Native GitHub sub-issue creation remains a remote synchronization step;
the repository retains deterministic drafts and Project rows as the source of truth.

## 2026-07-15 — OSF package prepared without remote mutation

Decision: Prepare and validate the OSF protocol/report component package, but keep every
sync-manifest row `publish_allowed: false` until the target OSF project and accountable
publication approval are confirmed.

Rationale: The package is reproducible and locally inspectable, but OSF upload is an external
mutation and registration/publication approval cannot be inferred from generated agent output.

Consequence: The OSF workflow remains dry-run safe; the final handoff records the remaining
credential/approval blocker and no OSF remote files are changed.

## 2026-07-15 — Hugging Face candidate validated without remote publication

Decision: Keep the Hugging Face dataset and Space candidate bundle unpublished until the
required repository targets, token and publication approval are explicitly configured.

Rationale: The local bundle passes its raw-path, secret, metadata and dashboard checks, but
bundle validity is not authorization to mutate an external dataset or Space repository.

Consequence: HF publication remains a documented secret-gated handoff task; no remote HF
repository is changed by local continuation work.

## 2026-07-15 — Zenodo deposition deferred behind evidence gates

Decision: Keep Zenodo deposition and DOI creation deferred until evidence, source licensing,
OSF protocol and human-review gates pass.

Rationale: The repository can produce a signed release candidate and citation metadata locally,
but an external DOI would imply archival/publication readiness that the current fail-closed
status does not support.

Consequence: Release metadata remains locally reproducible; no Zenodo record or DOI is created.

## 2026-07-16 - Create native issues for external release blockers

Decision: Create native GitHub issues [#255](https://github.com/edithatogo/reimbursement-atlas/issues/255)
for historical MBS/PBS coverage and [#256](https://github.com/edithatogo/reimbursement-atlas/issues/256)
for Zenodo DOI release. These issues mirror the generated Conductor drafts and make the remaining
licence, source-access and publication approvals actionable without changing any release gate.
## 2026-07-15 — Historical MBS archive inventory and OSF CLI refresh

Decision: Add a metadata-only inventory for historical MBS targets and pin the OSF
workflow to `osf-cli-go v1.0.0-rc.1` after an isolated install and help-contract check.

Rationale: The official MBS archive pages expose 343 historical file targets across 32
archive pages, spanning 1974 through 2026. Downloading or republishing those payloads
without source-specific terms review would violate the project's fail-closed data policy.
The newer OSF CLI provides the current supported command surface while remaining safe for
the existing dry-run workflow.

Consequences: The repository now tracks URLs, archive periods, file names and explicit
manual-review status in `data/seed/historical_mbs_archive_targets.jsonl` and derived
outputs. No historical raw payloads were downloaded or committed. The OSF workflow's safe
validation run passed, and remote OSF mutation remains disabled until project configuration,
protocol approval and manifest-native publication authorization exist.

## 2026-07-15 — HF secret provisioning and clean-checkout evidence refresh

Decision: Configure the GitHub `HF_TOKEN` secret for the existing dataset and Space targets,
validate both publication workflows in dry-run mode, and regenerate committed evidence with
the ignored raw cache absent.

Rationale: The HF workflow can now authenticate when publication is eventually authorized,
but token availability must not override licence, protocol, source-contract, evidence or
policy gates. Local raw caches must not influence committed validation outputs or generated
release metadata.

Consequences: HF and OSF dry-run workflows passed, all seven local external quality gates
passed, and PR #158 merged the cache-independent generated artefacts. `OSF_PROJECT_ID`,
human licence review, mapping adjudication and research approval remain required before
any external publication or policy claim.

## 2026-07-15 — Reclassify configured publication credentials as review gates

Decision: Treat Hugging Face and OSF handoff tasks as `blocked_review`, not
`blocked_secret`, after the HF dry run passed and the token-gated OSF provisioning run
created private project `q8cnx` with repository variable `OSF_PROJECT_ID` configured.

Rationale: Credentials and target infrastructure are now present, but neither credential
availability nor private-project creation authorizes publication, preregistration or a
policy claim. The remaining blockers are licence, protocol, methods, mapping and human
approval decisions.

Consequence: Generated final-handoff summaries now report zero missing-secret blockers;
publication workflows remain fail-closed and no raw or restricted source data is uploaded.

## 2026-07-16 — Redacted PBS multi-endpoint acquisition evidence

Decision: Record local PBS API acquisition evidence as a separate metadata-only artefact rather
than extending the source registry with a stale, schedule-specific raw endpoint.

Rationale: The v3 API requires selecting a published monthly schedule before fetching item and
fee pages. A static registry row can safely describe `/schedules`, but it cannot honestly encode
the selected schedule, pagination, response schema and checksums of a later reviewed extract.
The new validator records those facts without copying raw rows, leaking local paths or changing
the fail-closed licence/research review boundary.

Consequence: `data/derived/source_downloads/pbs_api_acquisition.*` is a citable acquisition
observation for schedule `4706`, not an evidence-ready PBS dataset. The generated dashboard,
publication manifest, data dictionary, research package and GitHub Project artefacts expose its
review status and provenance.

## 2026-07-16 — OSF CLI v1.0 command contract

Decision: Pin the OSF workflow to the stable `osf-cli-go v1.0.0` release and verify its
unauthenticated command/help contract before any credentialed OSF job can run.

Rationale: The stable release adds machine-readable output, node export, metadata validation,
storage and registration commands. Version metadata alone does not prove that the required
commands and safety flags are present, while invoking authenticated commands during a contract
check would unnecessarily expose credentials to a tooling probe.

Consequence: `scripts/check_osf_cli_contract.py` checks the immutable version and required help
markers without network IO or credentials. OSF reconciliation and publication remain separately
fail-closed behind manifest approval, protocol review and explicit publication authorization.

## 2026-07-16 — Deterministic research-package descriptors

Decision: Exclude Frictionless, RO-Crate and DCAT descriptor files from the publication
manifest used to generate those descriptors, and enforce two-run byte identity in tests.

Rationale: Including a descriptor in its own manifest causes its checksum and byte size to
depend on the previous generation. That makes committed metadata drift on every regeneration
and weakens reproducibility. The descriptors remain complete for the licence-reviewed derived
artefacts they describe; only self-referential metadata is removed.

Consequence: `write_research_package` now filters the three descriptor paths through a frozen
dataclass-safe manifest replacement. The focused test suite proves all three outputs are stable
across consecutive generations, while release and publication gates remain unchanged.

## 2026-07-16 — Responsive dashboard smoke matrix

Decision: Run the dashboard browser smoke suite against desktop and mobile Chromium profiles,
using CSS-pixel screenshots for comparable diagnostic bounds.

Rationale: A desktop-only browser check could not detect responsive regressions, while device
pixel scaling made the existing screenshot cap fail for otherwise valid mobile pages. The new
matrix gives automated coverage across the two supported layout profiles without pretending that
human visual, accessibility or cross-platform baseline approval has occurred.

Consequence: All 18 route/profile checks pass locally. Reviewed visual baselines and WCAG sign-off
remain explicit handoff gates.

## 2026-07-16 — GitHub advanced secret scanning state

Decision: Treat non-provider secret-pattern scanning and secret-validity checks as account-level
hardening work until the live GitHub settings API reports them enabled.

Rationale: Provider secret scanning, push protection and Dependabot updates are enabled, but an
idempotent repository API enablement attempt did not change the two advanced settings. Reporting
them as active would be inaccurate.

Consequence: Issue #191 tracks the limitation, the security documentation records the observed
state, and no release gate claims coverage that is not verified.

## 2026-07-16 — Pixi test task invocation

Decision: Invoke Python test suites through `python -m pytest` in Pixi tasks rather than relying on
the generated `pytest` console-script launcher.

Rationale: The local official Pixi environment had a stale console-script shebang pointing at a
deleted temporary checkout, while the environment's Python interpreter and pytest module were
healthy. Module invocation binds the task to the active environment and is robust to relocatable
environment paths.

Consequence: Unit, smoke, property, integration and end-to-end Pixi lanes all pass; issue #192
tracks the harness hardening and its generated Conductor/project rows.

## 2026-07-16 — Research-package hash refresh after CI-order generation

Decision: Refresh the committed Frictionless and RO-Crate descriptors after the CI-order generated
artifact chain updates the release-gate hashes.

Rationale: The release-gate files were current, but the descriptors still contained their prior
hashes. A replay proved the descriptors become stable after one refresh; committing that refresh
restores consistency without changing the self-reference exclusion or any publication gate.

Consequence: The descriptor replay is now byte-identical across consecutive runs, and the change
remains within `track_data_packaging_standards`.

## 2026-07-16 — Automated dashboard accessibility scan

Decision: Add axe-core accessibility analysis to the existing desktop/mobile Playwright route
matrix, while retaining human accessibility and cross-platform visual review as release gates.

Rationale: Route metadata and responsive smoke checks did not exercise WCAG rule coverage. An
automated axe-core scan provides repeatable violation detection across all public routes and both
supported layout profiles without claiming that automated checks replace human review.

Consequence: All 18 route/profile tests pass with zero axe-core violations. Issue #188 remains open
for human accessibility sign-off and reviewed visual baselines.

## 2026-07-16 — Research-package generation order in CI

Decision: Make `research-package` the final generated-artifact step after release-readiness and
seed-lake generation in the repository automation, data-smoke and deterministic-regeneration
workflows.

Rationale: Release-gate hashes can change when the SBOM or dashboard dependency graph changes. If
the package descriptors are generated before those final gates, they contain stale release-gate
hashes even though each individual generator is deterministic.

Consequence: CI now verifies the complete generation order and the committed descriptors are
refreshed against the final release-gate hashes.

## 2026-07-16 — Secret-scanning control scope

Decision: Track non-provider scanning and partner-pattern validity checks as separate GitHub security
controls rather than treating validity checks as coverage for generic non-provider patterns.

Rationale: The authenticated repository is user-owned and the live API reports both settings disabled.
GitHub's control model treats validity checks as applicable to supported partner patterns, while
non-provider pattern coverage is a separate security-configuration capability.

Consequence: Issue #191 remains open for account/security-configuration work, with no false-positive
claim that partner validity checks cover generic non-provider secrets.
## 2026-07-16 - Deterministic release manifest before Zenodo deposition

Decision: Add a deterministic `release-manifest.json` to the tagged GitHub release and attest it
with the existing release workflow, while keeping Zenodo deposition disabled pending publication
approval.

Rationale: Existing attestations covered distributions, source archives and SBOMs, but consumers
could not compare those subjects through one tag/commit-bound inventory. A manifest improves
software supply-chain verification without implying that source licensing, OSF registration,
evidence release or policy claims are approved.

Consequence: The release workflow now builds, attests, verifies and publishes the manifest. The
manifest contains only relative paths, sizes and SHA-256 values for release subjects; no raw
source payloads or credentials are introduced.
## 2026-07-16 - Offline consumer verification for release manifests

Decision: Provide a local, network-free verifier for the tagged release manifest before requiring
GitHub attestation verification.

Rationale: Consumers need a deterministic way to validate the downloaded subjects and expected
tag/commit before invoking remote provenance checks. This adds integrity verification without
confusing it with GitHub workflow provenance or research/publication approval.

Consequence: `scripts/verify_release_manifest.py` fails closed on malformed metadata, unsafe paths,
missing subjects, tag/commit mismatches and checksum changes.

## 2026-07-16 - Genomics coverage-price-restriction demonstrator linkage

Decision: Extend the typed policy brief with a coverage linkage summary for the genomics/pathology
demonstrator, while keeping coverage decisions and schedule items as separate denominators.

Rationale: The first demonstrator requirement is a coverage-price-restriction linkage, but the
available fixtures do not establish item-level equivalence. Reporting both sides with explicit
denominator and non-inference language improves policy usefulness without manufacturing evidence.

Consequence: The dashboard exposes the linkage summary, while the demonstrator remains
fixture-backed and human-review gated.
## 2026-07-16 - Fail-closed mapping review status

Decision: Add one generated mapping review status row that joins candidate, evidence,
gold-standard, negative-control and calibration counts for dashboard and publication consumers.

Rationale: The workbench already exposed each review surface separately, but consumers had to
infer the overall state. A single explicit row improves auditability while preventing candidate
crosswalks from being mistaken for approved or evidence-ready mappings.

Consequence: The status is always `review_required`, requires reviewer sign-off, and reports
`evidence_ready: false` until human adjudication occurs.

## 2026-07-16 - Close dashboard provenance and automated quality functions

Decision: Mark the dashboard provenance drill-down and automated experience-quality functions as
implemented, review-gated, while keeping public deployment as prototype.

Rationale: The routes, generated provenance surfaces, axe-core checks, performance budgets,
deep-link checks, browser smoke tests and retained visual evidence are implemented and passing.
Automated evidence cannot substitute for human cross-platform visual or assistive-technology
review, nor can it prove that a public deployment is live.

Consequence: Conductor and generated project artefacts distinguish implemented local capability
from the remaining human review and deployment-verification gates.

## 2026-07-16 - Deterministic Mojo tokenizer benchmark contract

Decision: Mark the fixed-width Mojo tokenizer implemented and review-gated after adding a
deterministic benchmark fingerprint; leave the fuzzy prefilter prototype.

Rationale: The tokenizer has a passing Mojo smoke gate and Python parity contract. Canonical
operation counts and SHA-256 fingerprints provide reproducible workload evidence without making
runner-specific timing claims. The fuzzy prefilter still lacks adjudicated gold-standard recall.

Consequence: The runtime track distinguishes a parity-backed tokenizer from the uncalibrated
candidate-generation prototype.

## 2026-07-16 - Enforce immutable action references at CI boundary

Decision: Add `func_action_sha_pin_policy_gate` as an implemented, non-mutating workflow gate.
The gate fails on external action tags, floating refs or unknown refs and permits only full
40-character commit SHAs, local actions and Docker references. Tag resolution and dependency
updates remain separate reviewable operations; the gate does not fabricate SHAs or mutate pull
requests.

## 2026-07-16 - Add cross-browser graph renderer fallback

Decision: Keep the Cosmograph renderer on Chromium/WebKit and provide an explicit generated-data
fallback on Firefox. Headless Firefox can fail during Cosmograph device initialisation even when
the page and graph CSVs are valid; the fallback prevents console errors while preserving node and
edge counts and links to the accessible table views. The browser matrix remains blocking and the
fallback is covered by the route smoke suite.
## 2026-07-16 - Promote public dashboard deployment after live Pages verification

Decision: Promote `func_dashboard_public_deploy` from `prototype` to `implemented`.
The repository has a SHA-pinned GitHub Pages workflow, an explicit project-site base-path
contract, a pre-upload asset-prefix validator, and a post-deploy live smoke check against
`https://edithatogo.github.io/reimbursement-atlas/`. This status describes the implemented
deployment mechanism and verified software surface only; it does not claim Hugging Face
publication, cross-platform visual approval, accessibility sign-off, research readiness or
policy-claim readiness. Hugging Face mirroring remains separately token- and review-gated.

## 2026-07-16 - Add scheduled action-pin maintenance

Decision: Promote `func_action_sha_pin_bot` to `implemented` with a fail-closed scheduled and
manual workflow that resolves complete action-pin sets and opens ordinary reviewable PRs.

Rationale: Immutable action refs are a supply-chain control, but silently mutating protected
branches would weaken provenance. The bot therefore refuses partial resolution, preserves
version comments, uploads resolver evidence and never writes directly to `main`.

Consequence: Future action updates remain subject to network availability, the generated
immutable-action policy gate and the repository's normal protected-branch checks.

## 2026-07-16 - Add fuzzy prefilter benchmark evidence

Decision: Add a deterministic benchmark for the Mojo/Python fuzzy-prefilter prototype without
promoting it to implemented.

Rationale: The synthetic reviewed fixtures currently produce recall, precision and specificity
of 1.0 at threshold 0.2, but the fixture is too small and synthetic to establish real-source
mapping performance. The benchmark makes this boundary visible rather than converting a local
prototype result into an evidence claim.

Consequence: Real reviewed mapping expansion and accountable human adjudication remain required
before promotion or evidence-readiness claims.

## 2026-07-16 - Add review-only historical and Zenodo automation

Decision: Add a scheduled metadata-only historical inventory refresh and a manual read-only
Zenodo preflight, while keeping historical payload acquisition and DOI creation externally gated.

Rationale: Archive drift and release metadata can be monitored safely in-repository, but source
licensing, reviewed PBS acquisition, research approval and DOI deposition remain accountable
human/publication decisions.

Consequence: The workflows open ordinary PRs or emit private preflight evidence only; they do
not download raw historical files, accept publication tokens or mutate Zenodo.

## 2026-07-16 - Enforce Hugging Face dataset-card metadata contract

Decision: Make the dataset-card contract a blocking repository data-smoke check while keeping
actual publication fail-closed.

Rationale: A versioned card must distinguish Apache-2.0 repository code from source-specific
data terms and must warn that only licence-approved manifest rows may be published. Presence of
a card alone is too weak to catch accidental licensing ambiguity.

Consequence: The validator checks metadata and disclosure markers on every pull request, but
human source-licence review, release readiness and HF credentials remain required for mutation.

## 2026-07-16 - Record authoritative MBS redistribution constraint

Decision: Treat MBS Online as public-to-access but not open-to-redistribute by default.

Rationale: The official copyright notice permits limited personal, non-commercial, unaltered
use and states that redistribution or commercial use requires prior written Commonwealth
approval. This is stricter and more useful than a generic `public` source label.

Consequence: The source registry, licence evidence document and MBS derived bundle retain the
`public_reuse_review` gate. Apache-2.0 remains limited to project-owned code and documentation;
PBS remains blocked pending authenticated acquisition and terms review.

## 2026-07-16 - Validate checksum-bound human licence decisions

Decision: Add a fail-closed validator for optional machine-readable licence decisions without
changing any current publication or review status.

Rationale: The generated queue already binds candidate artefacts to SHA-256 checksums, but a
future human decision record needs an automated check for stale artefacts, unknown identifiers,
missing reviewer evidence and invalid decisions. The validator makes that control executable
without inferring approval from source accessibility or queue generation.

Consequence: The current absent decision file remains valid and all candidate rows remain
pending. Any future approval or block record must include source terms, attribution,
redistribution permission, restrictions, evidence, reviewer and date, and must match the exact
queue checksum.

## 2026-07-16 - Verify GitHub advanced secret-setting boundary

Decision: Keep issue #191 open after authenticated API enablement requests returned `disabled`
for both non-provider secret-pattern scanning and partner-pattern validity checks.

Rationale: The repository already has full-history Gitleaks coverage, provider scanning and push
protection. The live settings API is authoritative for the two additional account-level controls;
claiming them enabled would be false security evidence.

Consequence: The repository-owned compensating control remains active, while the GitHub account or
plan capability remains an explicit external blocker.

## 2026-07-16 - Recheck GitHub advanced secret controls with JSON API payloads

Decision: Keep issue #191 open after retrying both advanced GitHub secret-control settings with
authenticated nested JSON PATCH payloads.

Rationale: The API accepted the requests but returned the repository with
`secret_scanning_non_provider_patterns=disabled` and `secret_scanning_validity_checks=disabled`.
The live response is stronger evidence than a successful request status and does not support
claiming the controls are active.

Consequence: No repository workflow change is needed. Provider scanning, push protection,
Dependabot and full-history Gitleaks remain the documented compensating controls.

## 2026-07-16 - Revalidate the July MBS reviewed pair

Decision: Refresh the derived provenance for the locally cached July 2026 MBS TXT pair, but keep
the bundle blocked from public redistribution.

Rationale: The raw pair is available in the ignored local cache and the reviewed-pair parser can
reproduce the derived item map and descriptor metadata. Reprocessing confirms the source-content,
source-contract, public-data-policy and licence-queue controls without treating access to MBS
Online as redistribution permission.

Consequence: Only redacted derived provenance timestamps changed in the tracked bundle and licence
queue. The MBS rows remain `public_reuse_review`; PBS current acquisition remains credential-gated.

## 2026-07-16 - Normalize Apache-2.0 code licence metadata

Decision: Use the canonical Apache-2.0 licence text in `LICENSE`, place project attribution and
the source-data boundary in `NOTICE`, and make the public-docs gate verify both files.

Rationale: Project metadata and README already declared Apache-2.0, but GitHub's live repository
metadata reported `Other/NOASSERTION`. Normalizing the standard text improves platform detection
and makes the code/data distinction executable without treating provider data as Apache-licensed.

Consequence: Code and project documentation remain Apache-2.0; underlying source terms remain
source-specific and governed by the licence-review queue.

## 2026-07-16 - Refresh non-mutating publication and source preflights

Decision: Rerun OSF discovery/plan, Hugging Face candidate validation, Zenodo preflight and
source-health monitoring against merged main without enabling any publication mutation.

Rationale: External credentials are configured in GitHub, but current evidence must be tied to
the merged commit and must distinguish automation readiness from human publication approval.

Consequence: OSF run `29475141289`, Hugging Face run `29475142574`, Zenodo run `29475143715`
and source-health run `29475144835` all passed. OSF/Hugging Face writes, Zenodo deposit and
DOI creation did not occur; PBS acquisition remains blocked by the absent approved secret.

## 2026-07-16 - Record stale Advanced Security zizmor check binding

Decision: Keep the `zizmor` requirement enabled, but rebind its required-check app from the
queued GitHub Advanced Security app `57789` to the passing repository-owned GitHub Actions app
`15368` through repository-admin settings.

Rationale: PR #274 has a passing SHA-pinned `zizmor` workflow, while the separately required
Advanced Security check is queued without an associated Actions run and blocks normal merging.
An authenticated REST update returned `404 Not Found`, so the setting cannot be changed through
the current API route.

Consequence: Issue [#275](https://github.com/edithatogo/reimbursement-atlas/issues/275) records
the exact app IDs and evidence. No security gate was removed and no administrator merge bypass
was used.

## 2026-07-16 - Resolve required zizmor check binding

Action: Used the repository-admin GraphQL `updateBranchProtectionRule` mutation to change only
the `zizmor` required-check app from `57789` to GitHub Actions app `15368`.

Evidence: The mutation returned all 20 required contexts with `zizmor` bound to
`github-actions`; the REST read-back reports `{context: zizmor, app_id: 15368}` and strict
status checks remain enabled. The REST write route returned 404 but was not needed after the
successful GraphQL update.

Consequence: Issue [#275](https://github.com/edithatogo/reimbursement-atlas/issues/275) is
closed. Branch protection remains strict and no required security gate was removed or bypassed.

## 2026-07-16 - Reconcile live GitHub Project issue coverage

Action: Audited live project #18 against the repository issue ledger and added missing items
for issues #131, #140, #237, #255, #256 and #275.

Evidence: Project item read-back shows closed issues #131, #140 and #275 as `Done`, and active
issues #237, #255 and #256 as `Todo`. No issue bodies, labels or status gates were weakened.

Consequence: The live board now covers the previously missing repository issue set. Local
generated project rows remain the deterministic reconciliation source for later updates.

## 2026-07-16 - Add branch-protection drift validator

Action: Add `scripts/check_branch_protection.py` and the `branch-protection-live` Pixi task.
The validator checks strict status checks, all 20 declarative contexts and the required
`zizmor` GitHub Actions app binding (`15368`) from either a captured API response or a live
authenticated request.

Evidence: The validator passed a fresh authenticated `main` branch-protection response, and
unit coverage now includes valid, missing-context and wrong-app fixtures. It performs no writes
and never prints bearer tokens.

Consequence: Future admin or scheduled audits can detect branch-protection drift before it
causes a queued or misbound required check. The validator is deliberately not itself a required
status context, avoiding a new circular branch-protection dependency.
The implementation is tracked in [#279](https://github.com/edithatogo/reimbursement-atlas/issues/279),
which was closed after PR #278 merged and the completed item was added to Project #18.

## 2026-07-16 - Verify pinned osf-cli-go release and local contract

Action: Checked the upstream `edithatogo/osf-cli-go` latest release and installed the pinned
`v1.0.0` binary into an ignored temporary directory for local verification.

Evidence: Upstream latest release is `v1.0.0`; the contract command passed with
`OSF CLI contract passed: osf 1.0.0`. No token values were read or logged and no OSF API
mutation occurred.

Consequence: The pinned OSF toolchain is current and reproducible. OSF registration, upload
and publication remain gated on protocol, licence, evidence and human approval.

## 2026-07-16 - Use the official PBS public-user key path

Decision: Treat the public `Subscription-Key` displayed by the official Department of Health API
catalogue as a runtime acquisition input for the PBS public API, without committing or logging
the value.

Evidence: A 2026-07-16 request to `/pbs/api/v3/schedules` with the current catalogue value and
`Accept: application/json` returned HTTP 200 and 10 schedules. The hardened repository downloader
then recorded the schedule response as downloaded with a redacted command.

Consequence: PBS live acquisition is executable without a private vendor credential. The API
schedule and existing items/fees extracts remain `acquired_unreviewed`; field/licence review and
promotion to a reviewed source bundle remain required.

## 2026-07-16 - Clarify licence queue population

Decision: Describe the 159-row licence queue as artifact candidates rather than source-derived
files.

Rationale: The queue intentionally includes project metadata, governance outputs, seed artefacts
and source-derived candidates. Calling all 159 rows source-derived overstated the external data
review workload, while removing the queue would weaken publication controls.

Consequence: Documentation and Conductor context now distinguish the total artifact queue from
the source-derived subset. All rows remain pending and publication remains fail-closed.

## 2026-07-17 - Merge toolchain evidence redaction after reproducibility validation

Decision: Merge the machine-path redaction and refresh the generated projections only after the
repository's deterministic regeneration and generated-artifact checks passed on GitHub.

Evidence: PR #311 merged as `bbb83e8770b8b73b3df8f3b817565eb7b1944328`. The post-merge local policy,
seed-sync, CLI, focused unit, Ruff and basedpyright checks also passed. The committed toolchain
report uses stable `PATH:<executable>` values and does not expose workstation-specific paths.

Consequence: Software release readiness remains true, while research publication, evidence release,
policy claims, source licensing and human review remain separate fail-closed gates.

## 2026-07-17 - Adopt compatible stack-canary dashboard updates

Decision: Upgrade the dashboard to `@cosmograph/react` `2.3.3` and Astro `7.1.0`, while retaining
TypeScript `6.0.3` until the pinned Astro checker supports TypeScript 7.

Evidence: Stack canary run `29526345487` passed Pixi, Python 3.14, external-quality, dependency,
dashboard-build and Mojo smoke steps. Local `npm ci`, `astro check`, static build and production
`npm audit` also passed. The canary opened issue [#360](https://github.com/edithatogo/reimbursement-atlas/issues/360)
for the three available updates; TypeScript 7 remains an explicit compatibility follow-up.

Consequence: The repository moves to the current compatible dashboard stack without using
`--legacy-peer-deps` in CI or silently converting a peer incompatibility into an accepted gate.

## 2026-07-17 - Refresh runtime-only PBS acquisition and MBS derived evidence

Action: Read the official Department of Health API catalogue through the browser route, used the
displayed public-user PBS key only in the acquisition process environment, reran the hardened
download plan, and reprocessed the local July 2026 MBS TXT pair.

Evidence: The refreshed redacted attempt ledger records three downloads and six intentional
`skipped_licence_gate` targets. The PBS key is absent from the worktree and generated command
provenance remains `[REDACTED]`. The MBS bundle parser produced 14,856 schedule items; source
validation, source contracts, licence-queue validation and repository release readiness remain
green while human redistribution review remains pending.

Consequence: The previous PBS credential blocker is resolved for this runtime session, but the
source-health gate remains partial because licence-gated historical/CMS targets must not be fetched
or promoted without accountable review.

## 2026-07-17 - Enforce administrator branch-protection checks

Decision: Enable administrator enforcement on the protected `main` branch without adding a second
reviewer requirement.

Evidence: GitHub REST read-back reports `enforce_admins.enabled=true`, strict required status
checks, linear history, conversation resolution, force-push protection and deletion protection.
Required pull-request reviews remain unset, so the solo-maintainer workflow is preserved without
weakening the CI and security gates.

Consequence: Administrators cannot bypass the required software-quality and supply-chain checks.
GitHub non-provider secret-pattern scanning and validity checks remain disabled by account/feature
availability; the attempted repository API enablement was ignored and is recorded on issue #191.

## 2026-07-17 - Enable repository-level GitHub Actions SHA enforcement

Decision: Enable GitHub's repository-level `sha_pinning_required` control after verifying that all
workflow action references are already immutable commit SHAs.

Evidence: The Actions permissions REST read-back reports `enabled=true`,
`default_workflow_permissions=read` and `sha_pinning_required=true`; the workflow reference audit
contains no tag-only action references. Issue [#352](https://github.com/edithatogo/reimbursement-atlas/issues/352)
was updated and closed as complete. The allowed-action policy remains unchanged at `all` so existing
pinned workflows continue to run without an unreviewed allowlist change.

Consequence: Future workflow changes using mutable action tags are rejected at the repository
control plane in addition to the repository's actionlint, workflow-policy and zizmor checks.

## 2026-07-17 - Recheck dashboard canary and TypeScript 7 compatibility

Decision: Close the resolved stack-canary drift issue without forcing TypeScript 7 into the current
Astro checker toolchain.

Evidence: The npm registry reports current compatible versions of Astro `7.1.0`,
`@cosmograph/react` `2.3.3` and `@astrojs/check` `0.9.9`. The checker declares
`typescript: ^5.0.0 || ^6.0.0`, while TypeScript `7.0.2` is the latest release. `npm ci`,
`astro check`, build and browser gates remain green on TypeScript `6.0.3`.

Consequence: Issue [#360](https://github.com/edithatogo/reimbursement-atlas/issues/360) is closed
as resolved. Issue [#362](https://github.com/edithatogo/reimbursement-atlas/issues/362) remains an
explicit compatibility blocker until the upstream checker peer contract supports TypeScript 7;
no unsupported peer override or `--legacy-peer-deps` path is used.

## 2026-07-17 - Refresh read-only Hugging Face destination drift evidence

Decision: Keep the existing Hugging Face Space unchanged after a read-only destination preflight
detected governed metadata drift.

Evidence: Workflow run `29529143659` reached both public targets. The dataset
`edithatogo/reimbursement-atlas` matches the candidate `license=other` contract. The Space with the
same identity is reachable but reports `license=mit` and `sdk=gradio`, while the governed candidate
requires `apache-2.0` and `static`; the checker reports `mutation_performed=false`.

Consequence: Issues [#320](https://github.com/edithatogo/reimbursement-atlas/issues/320) and
[#322](https://github.com/edithatogo/reimbursement-atlas/issues/322) contain the current evidence.
No remote correction is permitted until licence, evidence, research and policy gates pass and
publication is explicitly approved.

## 2026-07-17 - Verify the deployed public dashboard

Decision: Treat GitHub Pages as deployed and publicly verified for the current main commit, without
changing any evidence or publication readiness claims.

Evidence: Pages workflow `29529530333` passed build, dashboard quality, route, browser smoke,
artifact-prefix, deployment and post-deployment live-smoke gates for commit
`0ac2be4853aa2bbb896b22c0bf5e157e8c49ebb8`. The canonical site returned HTTP 200 and its deployed
`status.json` matched the tracked `apps/dashboard/public/status.json` byte-for-byte.

Consequence: The public product deployment is complete locally and externally observable. Evidence,
licence, research, OSF, policy and Hugging Face destination gates remain fail-closed until their
respective human review, credentials and explicit publication decisions are available.

## 2026-07-17 - Reconcile implemented issue lifecycle state

Decision: Close only GitHub issues whose generated Conductor status is `implemented` or `done` and
whose acceptance criteria contain no unchecked item.

Evidence: Issues #322, #328, #332, #333, #334, #335, #336, #337, #338, #355, #356 and #359 met
that rule and were closed. GitHub Project 18 read-back reports their rows as `Done`.

Consequence: Release-gated issues remain open, including source/licence review, evidence and
publication decisions, TypeScript 7 compatibility and the GitHub account-level secret controls.
Repository implementation completion is not treated as external approval.

The renderer contract is tracked in Conductor and issue [#370](https://github.com/edithatogo/reimbursement-atlas/issues/370);
the issue is closed as implemented and its Project 18 row is `Done`.

## 2026-07-17 - Merge generated issue status contract

Decision: Accept the status-aware generated issue renderer and its generated artefacts only after
the protected PR checks and the exact ordered regeneration harness pass.

Evidence: PR [#371](https://github.com/edithatogo/reimbursement-atlas/pull/371) merged as
`81edb376b0de517cae045a4e885417da5c97fc25`; generated-artifacts, deterministic-regeneration,
security, Python 3.14, dashboard and browser checks passed. Main was regenerated in CI order and
`git diff --exit-code` passed.

Consequence: Repository release readiness remains true, while external research, evidence,
licence, policy and publication readiness remain independently fail-closed.

## 2026-07-17 - Reconcile remaining implementation-complete GitHub issues

Decision: Synchronize and close only issues whose generated Conductor status is `implemented` or
`done` and whose generated implementation criteria are fully checked.

Evidence: Issues #326, #330, #339, #340, #341, #342, #343, #344, #345, #346, #351, #353 and #354
were synchronized from tracked drafts and Project 18 reports each as `Done`.

Consequence: Closure records repository implementation completion only. Licence review, source
review, research, evidence, policy and publication gates remain fail-closed in generated status.

## 2026-07-17 - Record real MBS acquisition without promotion

Decision: Treat the July 2026 MBS TXT pair as acquired local evidence and a derived parser fixture,
not as a reviewed or publishable source bundle.

Evidence: The governed curl plan recorded two successful downloads and seven gated/credentialed
targets. The derived MBS bundle contains 14,856 schedule rows, checksum-bound redacted snapshots,
no raw payload copies and `public_reuse_review` as its licence gate. Issue #23 was updated with the
evidence and remains open.

Consequence: Source validation and contract gates pass, but clinical review, licence review,
evidence readiness and publication readiness remain independently fail-closed.

## 2026-07-17 - Keep historical MBS expansion metadata-only

Decision: Advance historical coverage through an auditable archive inventory only; do not download
or mirror historical MBS/PBS payloads until target-specific terms and intended derived fields are
reviewed.

Evidence: The official MBS downloads and historical index pages were rechecked. The inventory has
343 targets across 32 archive pages, and issue #255 was updated with the evidence.

Consequence: Historical expansion remains a review gate and cannot be treated as evidence or
publication readiness.

## 2026-07-17 - Reconfirm Hugging Face destination drift

Decision: Treat the current Hugging Face Hub read-back as external destination evidence only;
do not mutate either target or infer publication approval.

Evidence: The configured dataset reports `license: other` and its README exposes an MIT-linked
metadata file. The configured Space reports `sdk: gradio`, while the governed candidate requires
Apache-2.0 code metadata and a static Space. No remote files, cards, metadata or settings changed.

Consequence: Issue #320 remains open. Licence, evidence, research, policy and explicit publication
approval gates remain independent blockers even though the local repository release gate is green.

## 2026-07-17 - Recheck GitHub account-level secret controls

Decision: Preserve issue #191 as blocked by GitHub account/plan capability after a fresh
authenticated settings attempt; do not represent the accepted PATCH request as enablement.

Evidence: The authoritative repository response continues to report non-provider secret-pattern
scanning and secret-validity checks as `disabled`. Provider scanning, push protection, Dependabot,
Gitleaks history scanning, CodeQL, zizmor, dependency review and protected CI remain enabled.

Consequence: The repository's compensating controls remain the enforceable local boundary. No
secret values or credentials were accessed, and no repository code change can resolve this
account-level limitation.

## 2026-07-17 - Refresh the pinned OSF CLI contract

Decision: Accept only the repository-pinned `osf-cli-go` `v1.0.0` binary as OSF workflow evidence;
do not treat the unrelated workstation `osf` `0.3.2` binary as equivalent.

Evidence: The pinned binary was installed into a temporary ignored directory and
`pixi run osf-cli-contract` passed. No OSF credentials were read and no remote project, node,
registration, file or metadata was changed.

Consequence: The CLI toolchain gate is green locally, while registration and publication remain
fail-closed pending protocol, licence, governance and human review approval.

## 2026-07-17 - Reconcile generated output issue bodies

Decision: Synchronize remote output-plan issue bodies from tracked generated drafts without
changing issue state or interpreting repository implementation as publication approval.

Evidence: Issues #114, #115, #116, #117, #118, #121, #347, #348, #349 and #350 now contain the
generated checked repository criteria and the appropriate unchecked promotion/review criterion.

Consequence: Conductor drafts and remote issue content agree. OSF, Hugging Face, Zenodo and
research publication gates remain open where their human, licence or credential requirements are
not satisfied.

## 2026-07-17 - Add generated GitHub issue-body drift detection

Decision: Extend the existing dry-run-by-default GitHub synchronizer to compare and optionally
update generated issue bodies, while preserving issue state and publication gates.

Evidence: The filtered dry run detected issue #370 body drift; an explicit body update was applied,
and the subsequent dry run reported only `present`. Focused project-handoff/unit tests passed.

Consequence: Future Conductor regeneration can expose stale remote issue content without silently
mutating it. Body writes require `--apply`; no issue closure, promotion or destructive operation is
introduced.

## 2026-07-17 - Retry transient GitHub issue-sync failures

Decision: Retry only transient GitHub CLI failures (HTTP 502/503/504 and timeout responses) up to
three attempts with bounded exponential backoff. Permanent failures still stop the synchronizer and
remain visible to the operator.

Evidence: The initial explicit body reconciliation updated 67 of 119 issues before a GitHub 504 at
issue #66. After the retry policy was added, the remaining bodies were reconciled and the dry run
reported `present: 172` with no pending actions.

Consequence: Large idempotent reconciliations are resilient to transient GitHub availability without
silently retrying permission, validation or other permanent errors. Issue state and Project
membership remain untouched.

## 2026-07-17 - Verify live source-health state

Decision: Treat the current GitHub source-health workflow as the authoritative acquisition status and
keep the PBS target fail-closed until its runtime key is supplied through the approved secret store.

Evidence: Workflow run [29538465869](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29538465869)
completed successfully. Validation, contract, drift and release gates passed; the acquisition report
classified exactly one target as incomplete and opened issue [#383](https://github.com/edithatogo/reimbursement-atlas/issues/383)
for the missing `PBS_API_SUBSCRIPTION_KEY`.

Consequence: The repository has current network-enabled evidence without treating an incomplete PBS
acquisition as a source-health failure or committing credentials/raw payloads. MBS remains acquired
but unreviewed, and CMS/historical targets remain governed by their licence/review gates.

## 2026-07-17 - Verify PBS credentialed acquisition

Decision: Store the current official public-user PBS subscription key only as the GitHub Actions
secret `PBS_API_SUBSCRIPTION_KEY`; do not place it in source, generated provenance, logs or bundles.
Keep source-health incomplete while historical MBS and CMS targets are intentionally skipped by their
licence gates.

Evidence: Authenticated `gh secret list` confirms the secret exists without revealing its value. Source-health
run [29539008697](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29539008697) passed and
recorded a successful PBS schedules download with `Subscription-Key: [REDACTED]`. The remaining
incomplete status is caused by six `skipped_licence_gate` records, not missing PBS credentials.

Consequence: The PBS transport credential boundary is resolved for the protected runner, while source
promotion remains fail-closed pending field/licence review and the separate MBS/CMS review decisions.

## 2026-07-17 - Recheck TypeScript 7 against current checker metadata

Decision: Do not force TypeScript 7 into the dashboard until the pinned Astro checker publishes a
compatible peer contract. Keep TypeScript `6.0.3` and reject `--legacy-peer-deps` or an unsupported
override.

Evidence: npm reports TypeScript `7.0.2` as stable and `7.1.0-dev.20260715.1` as the current next
build. `@astrojs/check@0.9.9` declares `typescript: ^5.0.0 || ^6.0.0`; a clean npm install probe
returns `ERESOLVE` on TypeScript 7 before `astro check` executes. Existing npm CI, dashboard build
and browser gates remain green on TypeScript `6.0.3`.

Consequence: The bleeding-edge candidate is documented and tracked, but reproducible CI is preserved
until upstream checker support exists. Issue #362 remains blocked for that explicit reason.

## 2026-07-17 - Refresh OSF read-only discovery

Decision: Treat OSF authentication and project configuration as verified, but keep all OSF mutation
and publication paths fail-closed until protocol, licence, methods and governance review is approved.

Evidence: Workflow run [29545432007](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29545432007)
passed the pinned `osf-cli-go` `v1.0.0` contract and OSF plan. Authenticated discovery listed 28
projects and found the existing private `Reimbursement Atlas` project `q8cnx`; the sync manifest
contained no publish-allowed rows. Provisioning, registration, upload and publication were skipped.

Consequence: OSF credentials, project variable and CLI are operational. The remaining OSF boundary
is human research/licence/governance approval, not repository authentication or toolchain setup.
