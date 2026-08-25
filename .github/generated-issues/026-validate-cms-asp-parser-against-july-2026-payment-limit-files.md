# Validate CMS ASP parser against July 2026 payment-limit files

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:parser, phase:1-slice, type:medicines, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The July 2026 ASP reviewed bundle parses successfully into 890 derived payment-limit records.
- [x] Raw payloads remain local and payment-limit values are not represented as net prices.
