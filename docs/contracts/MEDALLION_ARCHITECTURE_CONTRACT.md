# Medallion Architecture Contract

## Purpose

This contract aligns Reimbursement Atlas with the evidence boundaries used by
Global Medicines Atlas and Archive Govt NZ. Layer names describe provenance and
promotion state, not directory names or storage technologies.

## Layer semantics

| Layer | Contract |
|---|---|
| Bronze B0 | Versioned source index. A row does not prove acquisition, coverage, currency, or availability. |
| Bronze B1 | Append-only acquisition events, retrieval evidence, rights state, admission state, temporal identity, and content-addressed receipts. |
| Bronze B2 | Immutable source-native bytes or an immutable rights-constrained reference when bytes cannot lawfully be retained. |
| Silver | Source-faithful typed records. Native identifiers and meanings remain recoverable and no cross-jurisdiction equivalence is asserted. |
| Gold | Checksum-bound, reviewable cross-source mappings and analytical evidence promoted from Silver. |
| Platinum | APIs, dashboards, datasets, archives, and other presentation or publication products promoted from Gold. |

DuckDB, Parquet, LanceDB, graph tables, catalogues, and the seed lake are
rebuildable projections. They do not replace B1 event history or B2 evidence
identity and are not automatically assigned a medallion layer by their format.

## Identity and temporal rules

- SHA-256 binds every retained payload and promoted artifact.
- `retrieved_at` never substitutes for a missing source publication or effective date.
- Re-parsing does not change the identity of the acquired payload.
- Every derived artifact records its input artifact identities and checksums.
- Missing source coverage remains unknown or unobserved, never negative evidence.

## Rights and storage rules

- Raw bytes remain outside Git under ignored storage such as `data/raw_live/`.
- The ignored path is a cache, not evidentiary identity.
- B1 may be reconstructed from source-file validation, reviewed snapshot, and
  historical acquisition receipts; each lane must retain its own event identity.
- B2 admission requires a 64-character SHA-256 and byte size. Identical payloads
  are represented once by checksum even when multiple acquisition events observed them.
- Failed or unavailable retrievals remain B1 events and never create B2 evidence.
- Restricted bytes use a rights-constrained B2 reference in shareable evidence.
- Restricted descriptors, secrets, local absolute paths, and raw payloads never
  enter Silver, Gold, Platinum, public packages, or generated dashboards.
- Hugging Face, Zenodo, GitHub releases, and dashboards are output boundaries,
  not ingest origins or sources of truth.

## Promotion rules

Permitted transitions are:

1. B0 to B1 after an acquisition attempt is recorded.
2. B1 to B2 after fixity and admission checks.
3. B1 or B2 to Silver after parser, schema, rights, provenance, and source-contract checks.
4. Silver to Gold after mapping, quality, evidence, and accountable review gates.
5. Gold to Platinum after release, public-data, licence, evidence, and product gates.

A bounded Platinum contract may satisfy the evidence gate with a current,
checksum-bound Gold artifact and its scoped accountable review rather than the
global evidence-release gate. Such a promotion must pin the product, Gold input,
review, rights state, permitted scope, and prohibited claims; it must not change
global evidence, policy, research-publication, DOI, or archive readiness.

Global `evidence_release_ready` is derived only from the canonical release-readiness
gate matrix. Layer projections must not infer it independently from a subset of
evidence or research-question counts.

Layer skipping is prohibited. A blocked or rejected promotion is retained as
evidence and cannot be inferred as approval from a downstream artifact's
existence.

## Authoritative implementation

- Typed contracts: `src/reimburse_atlas/medallion.py`
- Exported JSON Schemas: `schema/*Medallion*.schema.json` and `schema/Bronze*.schema.json`
- Validation tests: `tests/unit/test_medallion_contracts.py`

The contract is compatible in meaning with the sibling repositories, but each
repository retains its source-specific rights, admission, and publication gates.
