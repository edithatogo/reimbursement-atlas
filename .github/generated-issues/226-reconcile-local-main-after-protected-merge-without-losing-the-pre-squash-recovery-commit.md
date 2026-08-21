# Reconcile local main after protected merge without losing the pre-squash recovery commit

Epic: `RAC-GATE-001` — Release gate reconciliation and external dependency closeout

Labels: type:repo-automation, type:release, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Any pre-squash local commit is retained on a named recovery ref before local main alignment.
- [x] Local main exactly matches origin/main after verification.
- [x] No destructive reset or unreviewed deletion is used.
