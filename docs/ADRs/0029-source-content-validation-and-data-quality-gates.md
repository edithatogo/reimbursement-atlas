# ADR 0029: Source content validation and data quality gates

## Status

Accepted.

## Context

The repo can generate hardened `curl`/`wget` plans, but a successful command does not guarantee that the content is usable. Failed web servers can return HTML pages, downloaded files can be empty, expected record counts can drift, and licence-gated files must not be handled as ordinary public downloads.

## Decision

Add generated source-content validation and table-level data-quality reports as first-class release gates.

Source-content validation must not expose absolute local paths or commit raw payloads. It may record redacted local references, byte sizes, checksums, record counts and validation status.

Data-quality checks must cover minimum row counts, unique ids, foreign-key integrity, generated artefact presence and publication-manifest safety.

## Consequences

The repo can now distinguish three states clearly:

1. network/download unavailable;
2. downloaded but content invalid or suspicious;
3. downloaded, validated and ready for reviewed-source bundling.

Future source-specific validators should extend this generic layer once real reviewed downloads are available.
