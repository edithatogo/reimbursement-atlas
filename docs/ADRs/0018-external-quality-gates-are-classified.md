# ADR 0018: Classify external quality gates honestly

Date: 2026-07-04

## Status

Accepted.

## Context

Some gates, especially vulnerability auditing, depend on external network services. Treating network failure as either success or ordinary failure is misleading.

## Decision

Add `scripts/run_external_quality_gates.py` and `src/reimburse_atlas/toolchain.py` to classify gates as `passed`, `failed`, `blocked_network`, `missing_tool`, or `timed_out`.

## Consequences

- `pip-audit` being installed but unable to resolve `pypi.org` is recorded as `blocked_network`.
- `npm audit` can pass independently.
- Pixi/Mojo availability is recorded separately from Python/Node package installation.
