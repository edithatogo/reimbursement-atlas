# Codex import and track-execution handoff

This document mirrors `conductor/handoff/CODEX_IMPORT_PROMPT.md` and exists inside the repository so future agents and contributors can reproduce the handoff.

Use the external prompt when starting from a `.git.bundle` file. Once the repository is restored, use these project-native sources of truth:

- `conductor/TRACKS.md`
- `conductor/tracks.yml`
- `conductor/context/CURRENT_FOCUS.md`
- `conductor/backlog.yml`
- `.github/generated-issues/`
- `data/derived/github_project/github_project_items.*`
- `docs/FINAL_HANDOFF.md`
- `data/derived/final_handoff/final_handoff_tasks.*`

The continuation agent should work through every implementable track, regenerate all derived governance artefacts after changes, and leave explicit blocker records for network-, credential-, licence-, or human-review-gated tasks.
