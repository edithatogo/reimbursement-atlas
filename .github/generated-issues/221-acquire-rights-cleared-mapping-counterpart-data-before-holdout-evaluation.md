# Acquire rights-cleared mapping counterpart data before holdout evaluation

Epic: `RAC-GATE-001` — Release gate reconciliation and external dependency closeout

Labels: type:mapping, type:data-source, type:licence, type:statistics, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] ATC/RxNorm/CMS ASP and other required counterpart records have source, version, licence and checksum evidence.
- [x] The candidate frame is real-source derived, deduplicated and frozen before review.
- [x] No fixtures are used to satisfy quotas.
