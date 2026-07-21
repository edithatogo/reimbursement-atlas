# Distinguish partial source acquisition from complete handoff status

Epic: `HANDOFF-018` — Final local continuation and GitHub Project handoff gates

Labels: type:data-quality, type:handoff, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Source-health evidence separates operational acquisition blockers from skipped_licence_gate rows with machine-readable counts.
- [ ] Licence-only review status remains publication-blocking but does not create a duplicate acquisition-outage issue.
- [ ] Focused tests cover incomplete, review_required and clear source-health states.
