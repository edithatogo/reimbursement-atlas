# Bind authoritative release documentation to the checked-out commit

Epic: `REL-001` — Release readiness and architecture gates

Labels: type:documentation, type:repo-automation, type:release, phase:hardening, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The documentation freshness gate resolves HEAD and verifies the authoritative handoff, release-readiness, OSF, Zenodo and current-focus documents contain one full commit from the checked-out history or an immediate PR base/parent.
- [x] Historical monitor snapshots remain clearly labelled as audit evidence rather than current release state.
- [x] A unit test and generated freshness report provide machine-readable evidence without exposing secrets or local paths.
