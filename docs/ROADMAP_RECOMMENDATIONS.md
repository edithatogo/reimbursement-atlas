# Consolidated roadmap recommendations

The roadmap is now represented in machine-readable seed tables and Conductor tracks:

- `conductor_tracks.*`
- `roadmap_functions.*`
- `dataset_candidates.*`
- `mapping_resources.*`
- `research_questions.*`
- `output_artifact_plans.*`
- `runtime_targets.*`

Implementation priorities:

1. Evidence-grade live-source ingestion.
2. Mojo kernel parity and benchmarking.
3. Python 3.14 CI target.
4. OSF protocols and reports.
5. Hugging Face dataset and Space deployment.
6. RO-Crate/Frictionless/DCAT/Zenodo packaging.
7. Human-in-the-loop mapping workbench.
8. First policy demonstrators.
9. GitHub Action SHA pinning and blocking zizmór.
10. Network-enabled pip-audit and official Pixi validation.
11. A canary update lane for Python 3.14 patch releases, current Node/Astro dependency bumps, and Mojo toolchain refreshes before they hit the main release branch.

## v15 implementation recommendation update

The immediate next step remains real-source ingestion, but v15 adds two practical prerequisites:

1. Run the hardened `download_commands.sh` in a network-enabled environment and retain raw files only in ignored local storage.
2. Use `protocol_status.csv` to prioritise OSF protocol completion before any analysis is described as preregistered or report-ready.

After first successful live downloads, implement source-specific validators for file size, row count, expected columns, expected code patterns, restricted-descriptor leakage and source-version drift.
