# ADR 0003: Restricted ontology local-only cache

## Status

Accepted.

## Context

UMLS, SNOMED CT, DSM-5, CPT and OMIM have licensing constraints. The project can support them without redistributing restricted data.

## Decision

Provide adapters for user-supplied local licensed files or services. Commit only mapping schemas, licence metadata, scripts and non-infringing derived metadata.

## Consequences

- Safer public repository and Hugging Face dataset.
- Some functionality requires user configuration.
- CI must use mocked or permissive fixtures.
