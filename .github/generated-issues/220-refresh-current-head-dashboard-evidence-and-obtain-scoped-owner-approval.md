# Refresh current-head dashboard evidence and obtain scoped owner approval

Epic: `RAC-GATE-001` — Release gate reconciliation and external dependency closeout

Labels: type:dashboard, type:accessibility, type:provenance, type:review, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] The automated packet is generated against the current main commit.
- [ ] Displayed values and provenance checks pass without restricted raw content.
- [ ] The accountable owner approves the exact packet hashes within the declared route/browser/provenance scope.
- [ ] Universal WCAG conformance and independent VoiceOver claims remain excluded.
