# ADR 0016: Full mutmut as nightly, not pull-request blocker

## Status

Accepted.

## Context

The repository now has enough source surface for mutmut to generate thousands of mutants. A full run is valuable but too slow for a normal interactive or pull-request validation loop.

## Decision

Keep full `mutmut run` in the scheduled mutation workflow and treat it as a nightly/manual quality signal. Fast pull-request gates remain Ruff, format, basedpyright, seed sync, public-data policy, tests with coverage, Bandit, uv build and dashboard build.

## Consequences

- Mutation testing remains part of the quality system.
- Pull requests are not blocked by a long-running gate while the parser/API/dashboard design is still moving quickly.
- Surviving mutants should become test-hardening issues after source contracts and first live-source bundles stabilise.
