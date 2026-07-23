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
- [x] Add deterministic release metadata and workflow attestation; Zenodo DOI creation remains
  gated on publication approval.

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
- [x] Add a grouped, checksum-bound licence review handoff packet; approval remains a human gate.
- [x] Regenerate the 44-screenshot, 64-test automated review packet against the final release
  candidate across Chromium desktop/mobile, Firefox and WebKit, binding every route, browser,
  viewport, screenshot, provenance assertion and prohibited-content result to the tested commit.
  Hosted run `30014543059` passed 64/64 tests and produced 44 screenshots; automated packet
  SHA-256 is `baf26fcdf1855447de472caa81d1418a3a8e3203fc54bbcf117ef3a08c211f3c`.
  (Issue #493)
- [x] Record the accountable owner review with exact browser, OS, assistive-technology, route,
  provenance and exception scope using `approved_within_scope`. Owner packet SHA-256 is
  `acfa8a605d88f1385a1672fc1852999dd2a35cff9caf207d9805a7c8a2e0ba96`;
  manual VoiceOver and universal WCAG conformance remain excluded. (Issue #493)
- [x] Reject incomplete, stale or universal-conformance dashboard review records in readiness and
  schema gates. (Issue #493)
- [x] Require a fresh commit-bound browser packet and scoped owner decision whenever dashboard
  routes, rendered evidence fields, provenance contracts or readiness values materially change.
  Ordinary non-dashboard changes remain governed by evidence-fingerprint validation rather than
  an overbroad universal accessibility claim. (Issue #493)
