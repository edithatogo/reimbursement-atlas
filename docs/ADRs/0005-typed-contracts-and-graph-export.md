# ADR 0005: Add typed derived-data contracts and graph export

Date: 2026-07-03

## Status

Accepted.

## Context

The initial scaffold had typed registries but no explicit contracts for parsed schedule items, coverage decisions or crosswalks. It also had static seed graph files but no code path to regenerate them.

## Decision

Add:

- `ProvenanceRecord`
- `ScheduleItemRecord`
- `CoverageDecisionRecord`
- `CrosswalkCandidate`
- `build_seed_graph()` and `write_graph_csvs()`
- CLI commands for source scoring, graph export and project snapshots.

## Consequences

Positive:

- derived rows have an auditable schema;
- graph seed files can be regenerated from registries;
- future parser work has a stable target contract;
- dashboard work can start before live ingestion.

Trade-offs:

- the contracts will evolve as real source parsers expose edge cases;
- some source-specific fields will need extension tables rather than forcing everything into one item table.
