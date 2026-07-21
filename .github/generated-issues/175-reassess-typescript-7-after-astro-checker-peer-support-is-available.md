# Reassess TypeScript 7 after Astro checker peer support is available

Epic: `HARNESS-021` — Layered harness engineering and deterministic regeneration

Labels: type:dashboard, type:quality, phase:hardening, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] The current Astro checker peer contract is documented as the reason TypeScript 7 is not adopted.
- [ ] The stack canary issue and dependency versions are linked in an auditable session.
- [ ] A scheduled read-only compatibility canary records the checker peer range and TypeScript 7 channel without mutating package files.
- [ ] The canary opens or updates this issue only when the checker peer contract admits TypeScript 7.
- [ ] The upgrade is re-tested with npm ci, astro check, build and browser gates before adoption.
