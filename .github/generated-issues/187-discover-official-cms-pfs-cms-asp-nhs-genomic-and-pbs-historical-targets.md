# Discover official CMS PFS, CMS ASP, NHS genomic and PBS historical targets

Epic: `HIST-002` — Historical source family catalog and public-only archival

Labels: type:data-source, type:automation, risk:licence, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Catalog discovery is deterministic, HTTPS-only and records the official archive page and direct URL.
- [ ] Duplicate filenames remain distinct through URL-stable target identifiers.
- [ ] PBS metadata-only and AMA-gated targets remain explicit rather than being silently omitted.
