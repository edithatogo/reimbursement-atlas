# Validate CMS ASP parser against July 2026 payment-limit files

Epic: `LIVE-001` — Reviewed live-source validation

Labels: type:parser, phase:1-slice, type:medicines, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] CMS ASP parser contract and synthetic fixture are implemented.
- [ ] July 2026 payment-limit payload is manually acquired into ignored local storage.
- [ ] Source terms, checksum and permitted payment-limit fields are reviewed.
- [ ] Parsed output is validated without treating payment limits as net prices.
