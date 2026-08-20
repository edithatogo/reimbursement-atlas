# Remove OSF registration from active readiness and publication gates

Epic: `OSF-DEPRECATION-001` — Retire OSF as an active destination

Labels: type:research, type:automation, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Release, Hugging Face, Zenodo, dashboard and handoff contracts do not depend on OSF.
- [x] OSF mutation and monitor workflows are retired.
- [x] Registration gqk4z remains immutable historical provenance.
- [x] Rights, evidence, claims and external publication remain independently gated.
