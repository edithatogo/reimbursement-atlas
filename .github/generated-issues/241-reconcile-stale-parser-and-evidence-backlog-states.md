# Reconcile stale parser and evidence backlog states

Epic: `BACKLOG-REC-001` — Backlog state reconciliation

Labels: type:repo-automation, type:data-quality, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Completed parser and source-review items derive implemented status from checksum-bound reviewed bundles and current licence decisions.
- [x] Credentialed current-source parity remains distinct from completed bounded parser validation.
- [x] Completed bounded analyses and approved claim packages are not represented as completed full reports, papers or preprints.
- [x] Generated issue and Project states match Conductor and live GitHub state.
