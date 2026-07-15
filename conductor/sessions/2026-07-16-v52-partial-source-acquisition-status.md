# v52 partial source-acquisition status

## Finding

The final handoff classified the source-download task as complete when only some planned targets
had downloaded. A source-file ID match alone also treated a PBS documentation target as the PBS
API target despite different target paths.

## Implemented

- Added `partial` to the typed final-handoff status contract.
- Compare both `source_file_id` and `target_path` when matching acquisition evidence.
- Keep `complete` for a fully acquired executable plan and `blocked_network` for no acquisition.
- Regenerated handoff, release-readiness, dashboard and seed-lake outputs.
- Documented the distinction in `docs/FINAL_HANDOFF.md` and current focus.
- Added the change to the HANDOFF-018 Conductor backlog.

## Current result

`final_source_downloads` is `partial`; the handoff summary reports 2 complete, 1 partial, 1
ready-local and 8 review-gated tasks.
