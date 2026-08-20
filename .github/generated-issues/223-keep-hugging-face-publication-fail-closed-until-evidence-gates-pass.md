# Keep Hugging Face publication fail-closed until evidence gates pass

Epic: `RAC-GATE-001` — Release gate reconciliation and external dependency closeout

Labels: type:huggingface, type:publication, type:licence, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Metadata, Croissant, dataset card, licence and identity parity checks pass.
- [x] Publication remains dry-run only while evidence or policy-claim readiness is false.
- [x] No token is stored in the repository.
