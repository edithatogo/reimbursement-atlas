# Session: v19 Codex handoff package

Purpose: Package the v18 repository as a Codex-ready git bundle with a covering prompt for local extraction, organisation and full Conductor track execution.

Changes:

- Added `conductor/handoff/CODEX_IMPORT_PROMPT.md`.
- Added `docs/CODEX_IMPORT_AND_TRACK_EXECUTION.md`.
- Added Conductor backlog items for Codex bundle import and track-execution continuity.
- Updated decision log with handoff-governance decision.
- Regenerated issue drafts and GitHub Project export after backlog change.

Expected continuation:

1. User downloads the git bundle or handoff package locally.
2. User places it in a folder.
3. User gives `CODEX_IMPORT_PROMPT.md` to Codex.
4. Codex restores the bundle, reads Conductor context, runs gates, then works through all implementable tracks.
5. Codex records any network, credential, licence, runtime or human-review blockers in release-readiness/final-handoff outputs.
