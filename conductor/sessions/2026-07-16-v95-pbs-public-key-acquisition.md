# Session v95: PBS public-key acquisition

## Evidence

- The official Department of Health API catalogue lists `PBS API PUBLIC - v3` and a public-user
  subscription key.
- The key was used only as a shell environment value and was never printed, committed or written
  to provenance.
- `/pbs/api/v3/schedules` returned HTTP 200 with 10 schedule records when requested with
  `Accept: application/json`.
- The repository downloader initially used a mixed JSON/CSV `Accept` header and received HTTP 415;
  the downloader now uses the PBS-compatible JSON media type.
- The hardened acquisition run records three downloaded targets and six intentional
  licence-gated skips. The PBS schedules command is redacted in tracked evidence.
- Source validation and source contracts pass; the PBS API evidence remains
  `acquired_unreviewed` with 14,870 source records across the cached schedule/items/fees evidence.

## Boundary

Acquisition is complete enough for local validation, not for public evidence. Human review of the
selected PBS fields, source terms and derived redistribution scope remains required before creating
a reviewed PBS bundle or changing any publication gate.
