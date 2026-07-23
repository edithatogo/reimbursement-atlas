# Automate verified git bundle and archive handoff export

Epic: `HANDOFF-018` — Final local continuation and GitHub Project handoff gates

Labels: type:release, type:handoff, type:repo-automation, phase:handoff, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] A repository-owned exporter creates a complete git bundle, tracked-only archive, redacted manifest and SHA-256 checksum file outside the checkout.
- [x] The exporter verifies the bundle and records only basenames, commit and fail-closed readiness booleans in the manifest.
- [x] Unit tests cover deterministic metadata, path-prefix rejection and absence of absolute paths in the manifest.
