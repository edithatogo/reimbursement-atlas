# Add crosswalk review queue view to Astro dashboard

Epic: `DASH-002` — Generated artefact dashboard tables

Labels: type:dashboard, type:mapping, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] The `/crosswalks/` route renders candidate mappings, review queue, evidence, gold-standard, and negative-control tables.
- [x] The view labels candidates as requiring domain review and does not imply mapping approval or evidence readiness.
- [x] Generated crosswalk assets are included in dashboard seed synchronisation and route checks.
