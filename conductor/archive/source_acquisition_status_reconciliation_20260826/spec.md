# Specification

## Objective

Prevent completed source-ingestion capability from being reported as incomplete solely because
historical breadth, source availability, or checksum-bound evidence promotion remains partial.

## Acceptance Criteria

1. Source-health evidence reports implementation and coverage status independently.
2. The scheduled monitor closes implementation issue #603 when capability is complete.
3. Coverage breadth, failed targets, and licence-review rows remain visible under #255 and generated evidence.
4. Raw payloads, credentials, and restricted descriptors remain excluded.
5. Focused, deterministic-generation, and hosted checks pass.
