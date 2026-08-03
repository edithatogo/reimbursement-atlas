# Reconcile local main after protected merge without losing the pre-squash recovery commit

Epic: `RAC-GATE-001` — Release gate reconciliation and external dependency closeout

Labels: type:repo-automation, type:release, status:in_progress

Status: `in_progress`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Any pre-squash local commit is retained on a named recovery ref before local main alignment.
- [ ] Local main exactly matches origin/main after verification.
- [ ] No destructive reset or unreviewed deletion is used.
