# Validate CMS CLFS parser against one public file without CPT descriptor redistribution

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:parser, risk:licence, phase:1-slice, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] A reviewed CLFS bundle parses successfully and records immutable source provenance.
- [x] Derived output excludes CPT/HCPCS identifiers and descriptor text under the restricted-local-only contract.
