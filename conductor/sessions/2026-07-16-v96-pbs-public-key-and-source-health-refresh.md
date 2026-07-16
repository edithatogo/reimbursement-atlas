# Session v96: PBS public-key acquisition and source-health refresh

## Current state

- PR #283 branch `codex/pbs-public-key-acquisition` contains the runtime-only PBS public-user key path.
- The official PBS v3 `/schedules` endpoint returned HTTP 200 during the 2026-07-16 runtime probe.
- The key value is not committed, logged, or included in handoff artifacts.
- `data/derived/source_health/acquisition_status.json` now reports `status=clear` and `incomplete_count=0`.
- The public dashboard status no longer reports the stale `source_acquisition` blocker.

## Controls

- PBS source terms and derived-field scope remain `public_reuse_review`.
- Human licence/domain review is still required before public evidence release.
- Historical Conductor notes describing an absent PBS credential remain historical evidence and must not override the current generated source-health report.
- PR #283 has all required checks passing and squash auto-merge enabled, but one approving GitHub review is still required.

## Handoff

- The current branch handoff is recorded in the `3f56135a4aa4` bundle/archive manifest outside the repository.
- Do not close the live source-health issue until the change is merged to `main` and the scheduled monitor confirms the same clear state.
