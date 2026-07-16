# Add dashboard views for source validation and data-quality checks

Epic: `DQ-001` — Data quality and evidence readiness gates

Labels: type:dashboard, type:data-quality, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Public dashboard routes expose source validation, data-quality, and drift tables from generated artefacts.
- [x] Dashboard assets are sanitised and checked for ignored raw-cache paths and absolute local paths.
- [x] CI regenerates and builds the dashboard before protected merges.
