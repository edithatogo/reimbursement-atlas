# Reassess TypeScript 7 after Astro checker peer support is available

Epic: `HARNESS-021` — Layered harness engineering and deterministic regeneration

Labels: type:dashboard, type:quality, phase:hardening, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: evaluate the current stable TypeScript release against the pinned Astro checker contract.
- [x] Licence and data-governance implications are checked; this is a toolchain-only change with no data publication effect.
- [x] Tests or validation evidence are defined: npm registry peer metadata and a clean npm dependency-resolution probe.
- [x] Documentation or Conductor context records the current compatibility boundary.
- [x] A scheduled read-only compatibility canary records the checker peer range and TypeScript 7 channel without mutating package files.
- [x] The canary opens or updates this issue only when the checker peer contract admits TypeScript 7.
- [x] TypeScript `7.0.2` is available, but `@astrojs/check@0.9.9` declares `typescript: ^5.0.0 || ^6.0.0`; npm rejects the unsupported tree.
- [ ] Upgrade `@astrojs/check` or its checker peer contract, then rerun `npm ci`, `astro check`, build and browser gates before adoption.
