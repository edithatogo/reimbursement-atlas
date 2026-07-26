# Retain MBS XML adapter as a legacy-format compatibility fixture

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:parser, phase:1-slice, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The fixture adapter remains explicitly synthetic and is not registered as a live-source parser.
- [x] The separate reviewed-source parser remains the only XML path for checksum-bound local MBS payloads.
- [x] Tests bind fixture output to explicitly synthetic provenance and prevent it from being represented as reviewed live evidence.
- [x] Documentation distinguishes current-release XML, historical TXT pairs and synthetic compatibility fixtures.
