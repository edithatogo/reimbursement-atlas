# Session 2026-07-17: Source-Health Timeout Evidence

## Objective

Ensure a failed live acquisition attempt still produces redacted validation,
drift, readiness and escalation evidence rather than terminating before those
steps run.

## Implemented

- Acquisition is now explicitly identified and `continue-on-error` is enabled.
- The workflow records the acquisition outcome in
  `data/derived/source_health/monitor_run_status.json`.
- Validation, source-contract, drift and release-readiness commands all run and
  record return codes even after acquisition failure.
- The final enforcement step remains fail-closed and reports the acquisition
  outcome plus any gate failures.
- The workflow contract test covers the new evidence-preservation boundary.

## Evidence

The 2026-07-17 live run timed out while fetching the July 2026 MBS item-map
after the configured curl retry and timeout budget. The workflow produced an
incomplete-acquisition report and synchronized the escalation issue, but skipped
the downstream gates. This change closes that observability gap without changing
network, licence, publication or source-payload policy.
