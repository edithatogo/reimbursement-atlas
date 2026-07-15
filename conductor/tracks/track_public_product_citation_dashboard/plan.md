# Implementation Plan

## 1. Citation and documentation

- [x] Correct `CITATION.cff` metadata and add a fail-closed validator.
- [x] Update README with current product status, citation instructions and source-data licensing
  boundaries.
- [x] Add citation metadata and public documentation claim validation to CI.

## 2. Status and dashboard product surface

- [x] Generate `apps/dashboard/public/status.json` from release, evidence, data-quality and source
  validation summaries.
- [x] Add executive status cards and explicit software/evidence/publication separation.
- [x] Add table search controls, CSV downloads and stable section anchors.
- [x] Add provenance navigation for source and mapping evidence surfaces.
- [x] Add automated axe-core accessibility, page-size, route/deep-link, performance-budget and
  desktop/mobile Chromium smoke gates; reviewed cross-platform pixel baselines and human
  accessibility sign-off remain follow-ups.
- [x] Add a post-deployment HTTPS smoke gate for the canonical GitHub Pages project site.
- [x] Retain Playwright screenshots, performance metrics and axe-core attachments as a review
  artifact; human cross-platform visual and accessibility approval remains required.

## 3. Publication automation

- [x] Add SHA-pinned GitHub Pages deployment workflow.
- [x] Keep Hugging Face Space publication manual and token-gated, with local bundle validation.
- [ ] Create signed release metadata and Zenodo DOI only after publication approval.

## 4. Validation and handoff

- [x] Add targeted tests for citation validation and status-manifest contracts.
- [x] Regenerate the machine-readable public status artefact.
- [x] Run the targeted local quality and dashboard gates.
- [x] Regenerate Conductor issue/project/dashboard artefacts after the full dashboard slice.
- [x] Record external blockers in final handoff and release-readiness outputs; external HF/OSF
  publication and human licence/research review remain fail-closed.
- [x] Prepare and validate non-depositing `.zenodo.json` metadata; DOI creation remains gated on
  publication approval.
- [x] Expose machine-readable blocker IDs, evidence paths and next actions in the public status
  manifest and dashboard.
