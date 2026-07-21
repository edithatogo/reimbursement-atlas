# Keep generated issue acceptance criteria and status synchronized

Epic: `DX-001` — Developer experience and release hardening

Labels: type:automation, type:repo-automation, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Roadmap issue drafts with implemented status render checked local implementation criteria rather than generic unchecked placeholders.
- [ ] Output-plan issue drafts preserve their source status and explicit external promotion gate.
- [ ] Focused tests cover roadmap and output-plan rendering contracts.
- [ ] Generated issue and GitHub Project artefacts are regenerated from the same source records.
- [ ] The GitHub synchronizer detects generated issue-body drift and only writes bodies with explicit --apply.
- [ ] Body synchronization never closes issues or changes external publication approval state.
