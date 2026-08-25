# Validate PBS API CSV parser against a reviewed monthly public extract

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:parser, phase:1-slice, type:medicines, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The reviewed monthly PBS extract parses successfully into 6,945 deduplicated derived records.
- [x] The current derived fields and checksums have licence decisions; credentialed API parity remains a separate track gate.
