# Session v65: source-health secret guidance

Date: 2026-07-16

## Change

- Source-health acquisition reports now extract missing credential names from redacted attempt
  evidence and include them in JSON, Markdown and CSV output.
- The current PBS follow-up identifies `PBS_API_SUBSCRIPTION_KEY`; secret values are never read
  into the report or rendered.
- Added regression coverage proving the secret value is absent from serialized output.

## Verification

- `pixi run python -m pytest tests/unit/test_source_health_report.py -q` passed: 4 tests.
- `pixi run source-health-report` regenerated the current report.

## Boundary

This makes the credential blocker actionable but does not create, retrieve or publish the
credential. The PBS secret must still be supplied through GitHub's approved secret store by an
authorized maintainer before the scheduled acquisition can complete.
