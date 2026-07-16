# Add readiness table views to Astro dashboard

Epic: `DASH-002` — Generated artefact dashboard tables

Labels: type:dashboard, phase:1-slice, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] The `/readiness/` route renders source, analysis, ingestion, licence, and release-readiness tables from generated dashboard-safe artefacts.
- [x] Route and dashboard asset contracts validate the generated CSV inputs without including raw restricted payloads.
- [x] Readiness views preserve the separation between repository, evidence, and publication readiness.
