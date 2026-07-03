# ADR 0004: Conductor context management

## Status

Accepted.

## Context

Future work is likely to be carried out by multiple agents and human contributors. The project needs persistent context that is both human-readable and machine-readable.

## Decision

Use `conductor/` as the canonical context layer containing project brief, canonical context, task map, decision log, source map, analysis map, open questions, agent handoff cards and session notes.

## Consequences

- Reduces agent drift.
- Makes planning decisions auditable.
- Requires regular updates as work proceeds.
