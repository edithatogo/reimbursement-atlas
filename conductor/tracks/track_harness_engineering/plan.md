# Implementation plan

- [x] HAR-01: Validate separate property, integration and end-to-end CI lanes
  (`31a9f76`).
- [x] HAR-02: Validate interpreter-bound test task invocation (`46207a3`).
- [x] HAR-03: Validate deterministic generated-output regeneration (`31a9f76`).
- [x] HAR-04: Validate bounded mutation testing controls (`88ff093`).
- [x] Review Fixes: Preserve the TypeScript 7/Astro peer incompatibility as an
  explicit blocked canary, not an unsafe dependency upgrade (`64d0664`).
- [ ] HAR-05: Adopt TypeScript 7 only after the Astro checker peer contract and
  full dashboard/browser gates pass.

## Blocker decision record

### TypeScript 7 compatibility

- **Option A (recommended):** keep the production dashboard on TypeScript 6,
  retain the read-only scheduled canary, and revisit when the checker peer
  range explicitly admits TypeScript 7. This preserves reproducible installs
  and avoids unsupported dependency resolution.
- **Option B:** open a separate upgrade branch when the canary reports
  `upgrade_available`, then require `npm ci`, `astro check`, build and the
  browser matrix before adoption. This is the planned contingency.
- **Option C (rejected):** force TypeScript 7 with peer overrides now. This
  would make the dependency contract non-authoritative and could invalidate
  dashboard, accessibility and browser evidence.

### Hosted checks

- **Normal path:** wait for the queued PR checks and merge only after the
  required exact-head checks pass.
- **Contingency:** if a check remains queued or infrastructure-fails beyond
  its normal execution window, capture the run URL and redacted conclusion in
  the handoff; do not bypass a required gate or archive the track as passed.
