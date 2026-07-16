# Add source-content validation gate for downloaded public files

Epic: `DQ-001` — Data quality and evidence readiness gates

Labels: type:data-quality, type:data-source, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Source-content validation is generated for the acquisition registry and runs in CI and source-health workflows.
- [x] Licence-gated, metadata-only, missing, and executable-source states remain distinct and fail closed.
- [x] Validation outputs are checksum/provenance-linked derived artefacts; raw live payloads remain ignored.
