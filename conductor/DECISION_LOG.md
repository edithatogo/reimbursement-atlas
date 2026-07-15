# Decision log

| Date | Decision | Status | Notes |
|---|---|---|---|
| 2026-07-03 | Use Conductor as project memory and agent handoff layer. | Accepted | See ADR 0004. |
| 2026-07-03 | Start with design-first repository rather than immediate ingestion. | Accepted | See ADR 0001. |
| 2026-07-03 | Use Polars, Arrow, DuckDB and LanceDB as analytical spine. | Proposed | See ADR 0002. |
| 2026-07-03 | Treat restricted ontologies as local-only user-supplied resources. | Accepted | See ADR 0003. |
| 2026-07-03 | Keep Mojo as performance-extension layer, not first implementation language. | Accepted | Avoid premature optimisation. |
| 2026-07-03 | Target GitHub plus Hugging Face dataset/Space deployment. | Proposed | Requires licence-gated publishing workflow. |

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
