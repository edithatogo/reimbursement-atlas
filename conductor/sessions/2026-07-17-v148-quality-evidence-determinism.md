# v148 quality evidence determinism

## Problem

Passing quality-gate records included machine-dependent command output, causing deterministic
regeneration and generated-artifact checks to disagree across local and GitHub runners.

## Change

- Blank stdout/stderr excerpts for `passed` quality gates.
- Preserve diagnostic excerpts for all non-passing statuses.
- Add unit coverage for both behaviours.
- Regenerate downstream dashboard, data dictionary, licence-review, research-package and seed-lake
  artefacts.

## Evidence

- PR #390 initially failed deterministic and generated-artifact gates.
- After the fix, both passed, along with browser, build, readiness, security and test gates.
- Local quality profile: 27/27 passed.
- Focused tests: 278 passed.

## Boundary

This hardens software reproducibility only; it does not change evidence readiness, licensing,
research approval or external publication decisions.
