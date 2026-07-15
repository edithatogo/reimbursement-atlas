# Session v60: Source health escalation

Date: 2026-07-16

## Objective

Make incomplete source acquisition visible as a recurring operational item without
conflating acquisition blockers with licence or human-review decisions.

## Implemented

- Added the deterministic `source-health-acquisition-v1` report.
- Added unit coverage for partial, credential-blocked, clear and missing-handoff states.
- Added the `source-health-report` Pixi task.
- Extended the scheduled source-health workflow to upload acquisition evidence and
  open/update/close a dedicated `Source acquisition monitor: incomplete targets` issue.
- Documented the fail-open issue lifecycle and the no-network/no-mutation boundary.

## Acceptance evidence

- Source-ingestion statuses `partial`, `blocked_network` and `blocked_secret` are
  escalated.
- `blocked_review` is intentionally excluded because it requires licence or human
  judgement rather than acquisition automation.
- Missing generated handoff evidence produces `unknown`, never a false `clear`.
- The report contains no raw source payloads, credentials or absolute local paths.

## Remaining external gates

The report does not resolve PBS credentials, source licensing, human review, OSF
registration, Hugging Face publication or preservation deposits. Those remain explicit
handoff items.
