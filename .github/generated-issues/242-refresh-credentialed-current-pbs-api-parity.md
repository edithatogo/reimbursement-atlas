# Refresh credentialed current PBS API parity

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:data-source, type:parser, phase:implementation, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Acquire a current monthly PBS API extract into ignored local storage using the hardened acquisition layer.
- [x] Validate schema, effective-date semantics, deduplication and permitted derived fields against the reviewed monthly bundle.
- [x] Record redacted acquisition receipts and immutable checksums without publishing raw payloads.
- [x] GitHub Actions source-health run 32951770117 acquired three PBS API endpoint families with 14,867 source records and zero schema failures.
- [x] Redacted receipts contain no raw payloads, credentials or local paths; the reviewed 6,945-record monthly bundle remains the bounded derived comparison source.
