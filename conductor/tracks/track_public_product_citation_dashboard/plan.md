# Implementation Plan

## 1. Citation and documentation

- [x] Correct `CITATION.cff` metadata and add a fail-closed validator.
- [x] Update README with current product status, citation instructions and source-data licensing
  boundaries.
- [ ] Add citation and documentation freshness checks to CI.

## 2. Status and dashboard product surface

- [x] Generate `apps/dashboard/public/status.json` from release, evidence, data-quality and source
  validation summaries.
- [ ] Add executive status cards and explicit software/evidence/publication separation.
- [ ] Add table search controls, CSV downloads and stable section anchors.
- [ ] Add provenance navigation for source and mapping evidence surfaces.
- [ ] Add automated accessibility, performance and visual-regression gates.

## 3. Publication automation

- [ ] Add SHA-pinned GitHub Pages deployment workflow.
- [ ] Keep Hugging Face Space publication manual and token-gated, then validate the deployed Space.
- [ ] Create signed release metadata and Zenodo DOI only after publication approval.

## 4. Validation and handoff

- [ ] Add targeted tests for citation validation and status-manifest contracts.
- [x] Regenerate the machine-readable public status artefact.
- [x] Run the targeted local quality and dashboard gates.
- [ ] Regenerate Conductor issue/project/dashboard artefacts after the full dashboard slice.
- [ ] Record external blockers in final handoff and release-readiness outputs.
