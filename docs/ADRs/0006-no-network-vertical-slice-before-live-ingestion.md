# ADR 0006: No-network vertical slice before live ingestion

Date: 2026-07-03

## Status

Accepted.

## Context

The project needs to move from design to implementation, but live reimbursement data brings source-shape drift, licensing, copyright, provenance and hidden-price risks. A premature live scraper could make the repo brittle or unsafe to publish.

## Decision

Implement a complete no-network vertical slice using synthetic fixtures and conservative derived contracts:

- `ScheduleItemRecord`
- `CoverageDecisionRecord`
- `CrosswalkCandidate`
- `IngestionTaskRecord`
- readiness tables
- dashboard-safe CSV exports

Promote parser status from stubbed to prototype only for fixture-backed parsers.

## Consequences

Positive:

- the architecture is executable;
- CI can validate contracts without internet access;
- contributors can understand the intended data flow quickly;
- restricted source text and ontology dumps stay out of the public repo.

Trade-offs:

- policy outputs remain demonstrations until live source validation is completed;
- parser flexibility must be tested against real files before production use;
- apparent crosswalk quality is not meaningful until seeded with reviewed real examples.
