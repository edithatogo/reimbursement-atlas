# Plan

- [x] Define canonical external-control records and fail-closed normalization tests. (`4a74b847`)
- [x] Implement deterministic governance-monitor generation. (`4a74b847`)
- [x] Project external controls into release readiness as non-required gates and test readiness isolation. (`4a74b847`)
- [x] Integrate both scheduled monitors and repository generation workflows. (`4a74b847`)
- [x] Regenerate Conductor, GitHub Project, dashboard, readiness, package and handoff artefacts.
- [x] Run full local and deterministic validation; archive the exact head for protected hosted validation.

## 2026-08-30 compatibility recheck

The native `pixi run typescript-compatibility` network check on merged main
`f82c47b8` reproduced the tracked `blocked_peer` report without a diff or dependency
mutation: candidate TypeScript 7.0.2, installed 6.0.3, Astro checker 0.9.10 with
peer range `^5.0.0 || ^6.0.0`. Keep issue #362 open and the existing scheduled
canary enabled. This external compatibility boundary is not a repository release
blocker. No compatibility shim or weakened typing is introduced.
