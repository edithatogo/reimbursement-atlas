# Bronze Evidence Alignment

## Overview

Implement the B0 source index, B1 append-only acquisition ledger, and B2
immutable-evidence projection defined by the repository medallion contract.

## Requirements

- Project existing source registry rows into B0 without claiming acquisition.
- Project acquisition evidence into append-only B1 events with temporal, rights,
  admission, and content identity.
- Represent B2 as immutable bytes or a rights-constrained immutable reference.
- Treat local raw paths, DuckDB, Parquet, and publication destinations as
  storage or projection details rather than evidentiary truth.
- Preserve missing coverage as unknown or unobserved.

## Acceptance Criteria

- Deterministic B0/B1/B2 JSONL, CSV, summaries, and schema validation exist.
- Every retained-byte B1/B2 row is checksum-bound and every restricted row is reference-only.
- No generated public artifact contains a raw path or restricted payload.
- Unit, property, public-data, deterministic-regeneration, and Python 3.14 gates pass.

## Non-functional Constraints

- Raw payloads remain ignored and local.
- Generation is deterministic and fail closed.
- Existing source-specific licence decisions remain authoritative.

## External Gates

None. This track records repository evidence and does not authorize source
acquisition, licence promotion, or publication.

## Out of Scope

- Durable cloud object storage.
- New source acquisition.
- Silver, Gold, or Platinum promotion.

## Authoritative Inputs

- `docs/contracts/MEDALLION_ARCHITECTURE_CONTRACT.md` at contract commit `d67bbfac`.
- Global Medicines Atlas medallion contract at commit `72d03294fa9dfb3560b44303068660b43e35bb75`.
- Archive Govt NZ remote baseline at commit `be8878f785d34ec902503d09555de7dc4a727b55`.
