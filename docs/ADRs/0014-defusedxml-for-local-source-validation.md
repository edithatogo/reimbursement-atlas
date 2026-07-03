# ADR 0014: Use defusedxml for XML-like reimbursement sources

## Status

Accepted.

## Context

MBS and other public schedule sources may be distributed as XML or XML-like files. Even when files are manually downloaded from public sources, parsers should not normalise unsafe XML practices.

## Decision

Use `defusedxml.ElementTree` for XML fixture and local-source parsing. Treat local raw files as untrusted until snapshotted, checksummed, parsed into derived records and reviewed.

## Consequences

- XML parser prototypes are safer by default.
- Bandit no longer flags stdlib XML parsing in source code.
- Future live-source validation can reuse the same parser contract without relaxing security posture.
