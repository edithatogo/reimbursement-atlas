# Bronze Acquisition Coverage Expansion

## Overview

Expand B1 acquisition events and B2 immutable evidence from real historical
downloads and reviewed-source snapshot receipts while retaining B0 as catalogue identity.

## Requirements

- Restore reachable historical payloads only from allowlisted official HTTPS hosts.
- Verify byte size and SHA-256 before recording acquired evidence.
- Preserve failed acquisition attempts in B1 and exclude them from B2.
- Deduplicate B2 by payload checksum.
- Preserve source-specific rights states without treating acquisition as reuse approval.
- Exclude raw cache paths, absolute paths, source bytes, and transfer diagnostics from B1/B2.

## Acceptance Criteria

- B1 and B2 materially exceed the previous 11 and 3 records using real receipts.
- Every B2 record has a valid checksum, byte size, source version, and rights state.
- Unavailable historical targets remain explicit failed B1 attempts.
- Repeated generation is deterministic and public-data policy passes.
- Local and hosted quality, security, browser, readiness, and generation gates pass.

## External Gates

Source reuse and publication remain independently licence- and evidence-gated.

## Out of Scope

- Committing or redistributing raw payloads.
- Treating catalogue presence as acquisition.
- Publishing datasets, archives, papers, or preprints.
