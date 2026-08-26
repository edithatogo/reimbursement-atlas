# Reassess TypeScript 7 after Astro checker peer support is available

Epic: `HARNESS-021` — Layered harness engineering and deterministic regeneration

Labels: type:dashboard, type:quality, phase:hardening, status:monitored

Status: `monitored`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] The current Astro checker peer contract is documented as the reason TypeScript 7 is not adopted.
- [x] The stack canary issue and dependency versions are linked in an auditable session.
- [x] A scheduled read-only compatibility canary records the checker peer range and TypeScript 7 channel without mutating package files.
- [x] The canary opens or updates this issue only when the checker peer contract admits TypeScript 7.
- [x] The upgrade is re-tested with npm ci, astro check, build and browser gates before adoption.
- [x] Unsupported upstream compatibility is represented as a non-required release warning, never a repository release blocker.
