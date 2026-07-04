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

