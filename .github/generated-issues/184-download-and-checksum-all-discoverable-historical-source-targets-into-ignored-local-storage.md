# Download and checksum all discoverable historical source targets into ignored local storage

Epic: `HIST-001` — Historical source archival and reproducibility

Labels: type:data-source, type:automation, risk:licence, phase:implementation, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Acquisition is HTTPS-only, retrying, resumable and allowlisted to official hosts.
- [x] Raw payloads remain ignored and every target has a relative cache path, byte count and SHA-256.
- [x] Failures and cached files remain explicit in a generated manifest.
