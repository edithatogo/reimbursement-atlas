# Session v124: source acquisition refresh

## Scope

Refresh evidence-grade acquisition for executable public targets and reprocess the reviewed MBS
pair without tracking raw source payloads or credentials.

## Evidence

- The official Department of Health API catalogue was opened through the browser route.
- The public-user PBS `Subscription-Key` was used ephemerally and was not written to disk,
  generated metadata or Git history.
- `pixi run source-download-attempt` recorded three downloaded targets: two July 2026 MBS TXT
  files and PBS v3 schedules.
- Six historical/CMS targets remained explicitly `skipped_licence_gate`.
- The MBS pair workflow produced 14,856 derived schedule-item records and refreshed redacted
  source snapshots.
- Source validation, source contracts, source-health, licence-review validation, data-quality,
  evidence-readiness and release-readiness were regenerated. Release readiness remains 36/36;
  research/publication/evidence/policy gates remain fail-closed.

## Safety boundary

No raw payloads, subscription key, absolute local paths or licence-gated CMS content were added
to Git. The PBS and MBS outputs remain acquired/unreviewed or public-reuse-review candidates until
accountable source-term and licence decisions are recorded.
