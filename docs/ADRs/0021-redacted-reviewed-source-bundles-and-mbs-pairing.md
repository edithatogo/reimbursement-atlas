# ADR 0021: Redacted reviewed-source bundles and MBS TXT pairing

## Status

Accepted.

## Context

Reviewed-source bundles are the bridge from synthetic fixtures to manually downloaded public source files. Earlier bundle metadata preserved local raw paths in `source_snapshots.*`, which is useful locally but unsafe for public derived datasets or dashboard artefacts. The current MBS TXT path also requires two files, because item descriptors and item-map/payment-like fields are separate.

## Decision

1. Redact `local_path` in reviewed-source bundle snapshot exports by default.
2. Keep checksums, byte sizes, source version ids and licence/cache scopes in bundle snapshot records.
3. Add a dedicated MBS TXT-pair bundle command that snapshots both files, parses the joined derived rows, and writes pair-specific validation statistics.
4. Keep raw files in ignored local cache locations only.

## Consequences

Bundles are safer to inspect, share internally and evaluate for publication because they avoid leaking local filesystem paths. MBS live validation now has a source-specific pair workflow rather than forcing the general one-file reviewed-source command.
