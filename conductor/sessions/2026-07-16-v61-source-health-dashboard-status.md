# Session v61: Source health dashboard status

Date: 2026-07-16

## Objective

Expose the source-acquisition escalation report through the public status and dashboard
surfaces so maintainers do not need to inspect CI artifacts to see incomplete acquisition.

This extends the source-health automation tracked in GitHub issue #172.

## Implemented

- Added a dashboard-safe `acquisition_status.csv` projection.
- Added source-health evidence to the public status manifest.
- Made the public acquisition blocker use the report's `incomplete` or `unknown` status.
- Added the source acquisition health table to the automation dashboard page.
- Added contract coverage for the new status evidence path.

## Safety boundary

The dashboard exposes derived status only. It contains no raw live-source payloads,
credentials, local absolute paths or licence-gated descriptors, and does not perform
network I/O or source-cache mutation.
