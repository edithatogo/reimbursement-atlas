# ADR 0001: Design-first architecture

## Status

Accepted.

## Context

Comparative reimbursement analysis is vulnerable to false equivalence, source drift, licensing issues and over-engineering. Building ingestion before requirements are clear would create technical debt.

## Decision

Start with Conductor context, requirements, source registry, analysis catalogue, ontology strategy, seed schemas and dashboard scaffold before production ingestion.

## Consequences

- Slower initial code output.
- Better safety around licences and comparability.
- Easier handoff to future agents and collaborators.
