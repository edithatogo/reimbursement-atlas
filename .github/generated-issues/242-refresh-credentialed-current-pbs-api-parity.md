# Refresh credentialed current PBS API parity

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:data-source, type:parser, phase:implementation, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Acquire a current monthly PBS API extract into ignored local storage using the hardened acquisition layer.
- [ ] Validate schema, effective-date semantics, deduplication and permitted derived fields against the reviewed monthly bundle.
- [ ] Record redacted acquisition receipts and immutable checksums without publishing raw payloads.
