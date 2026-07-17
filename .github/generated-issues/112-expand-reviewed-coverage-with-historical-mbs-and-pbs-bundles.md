# Expand reviewed coverage with historical MBS and PBS bundles

Epic: `TRACK_LIVE_SOURCE_INGESTION` — Evidence-grade live source ingestion

Labels: type:roadmap-function, priority:must, interface:data_pipeline, status:planned

Status: `planned`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: metadata-only inventory automation and a target-level review packet are implemented; raw bundle acquisition remains gated.
- [x] Licence and data-governance implications are checked: historical targets remain manual-review only.
- [x] Tests or validation evidence are defined: `pixi run historical-sources`, source validation and source contracts.
- [x] Documentation or Conductor context is updated.
- [ ] Source-specific licence approval and reviewed PBS extract are complete.
- [ ] Historical raw payloads have been acquired into ignored local storage and promoted to reviewed derived bundles.
