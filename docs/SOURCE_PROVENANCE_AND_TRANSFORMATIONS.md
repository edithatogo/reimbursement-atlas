# Source Provenance and Transformations

This document is the human-readable companion to the machine-readable source registry,
snapshot records, publication manifest and per-record `ProvenanceRecord`. It defines the
reproducibility minimum for every source used in the atlas.

## Reproduction minimum

Every acquired source must have:

1. the exact provider URL or API endpoint;
2. the provider release/effective date and source-version identifier;
3. retrieval timestamp, content type, byte count and SHA-256 checksum;
4. the applicable licence terms, attribution and redistribution decision;
5. the parser name and versioned transformation description;
6. the output contract, excluded fields and validation results; and
7. a link from source snapshot to derived artefacts and research outputs.

Raw payloads remain in ignored `data/raw_live/` storage. Public artefacts contain provenance
metadata and derived fields only.

## Current source transformations

| Source | Exact input | Transformation | Public boundary |
| --- | --- | --- | --- |
| MBS current release | July 2026 XML, `au_mbs_20260701_xml` | Parse `Data` records; map `ItemNum`, `Category`, `Group`, `Description`, `FeeStartDate` and `ScheduleFee` to `ScheduleItemRecord`; normalise dates and amounts | Candidate derived fields only; raw XML and unrestricted descriptor redistribution excluded until source review |
| MBS historical/full map | July 2026 item-map plus descriptor TXT pair | Parse both files; join on MBS item code; retain joined rows and flag descriptor-only rows | Raw TXT excluded; descriptor-only rows require separate treatment |
| PBS | v3 schedules/items/fees or official CSV fallback | Validate endpoint schemas; join item rows to `/schedules` by `schedule_code`; derive effective date; reduce to the typed schedule contract; deterministically retain the first presentation per PBS item code for mapping-study sampling; label prices as schedule/list or payment values | Owner-approved bounded derived fields with source attribution and bundle/input checksums; raw payloads, headers, credentials, confidential net-price claims and unapproved fields excluded |
| CMS CLFS | CY 2026 Q3 V1 CSV, SHA-256 `f5a090789c40fe791b478a735c7cf5399e86726adc788f11829435cb0ca4d7d5` | Skip the CMS preamble; parse 2,206 rows; replace source identifiers with deterministic synthetic row identities; retain payment amount and effective date; exclude CPT/HCPCS identifiers and all descriptor fields | Restricted derived-only bundle; raw ZIP/CSV remain ignored and are not redistributed |
| CMS PFS | RVU26C July 2026 archive, SHA-256 `d45a158e02694c1539e7f88192c611883e377181eda86dc213359707bcacbacb` | Validate the expected `PPRRVU2026_Jul_nonQPP.csv` member and embedded AMA notice; parse numeric RVUs/payment inputs; optionally rank MBS-to-CPT hypotheses using descriptor text only in ignored local storage | Public outputs contain release identity, checksums, counts, parameters and restrictions only; CPT descriptors and descriptor-bearing candidates are never committed or published |
| CMS ASP | Exact July 2026 payment-limit release | Parse payment-limit fields and permitted crosswalk metadata | Candidate payment fields only; no coverage or net-price claims pending source review |
| CMS MCD | NCD export dated 20 July 2026, archive SHA-256 `3901cd99dd9e27ca3ee562a2329e45435c8e2ed1019b68d60d376a9483edc8e0` | Extract the nested CSV; retain NCD identity, version, title, effective date, national flag and termination flag; exclude long HTML document text | NCD metadata supports bounded coverage-document analysis only; it does not establish item-level coverage |
| NHS Genomic Test Directory | Rare and inherited disease v9 workbook, SHA-256 `2bd3a3e75e30d3e8c6b6623824cc8018f65b0e7fc0e24ced15d02beba9b43bf1` | Validate the named sheet and required columns; map commissioned clinical indication, test ID, method and category to `CoverageDecisionRecord` | A directory listing is represented as restricted commissioned availability, not universal patient eligibility |
| NHS Payment Scheme | 2026/27 Annex A workbook, SHA-256 `b227defd1f54b7836558a92d875905f0fa4e7cb27951539d142ad36cc6712d0d` | Validate the genomics guide-price sheet at its labelled header row; emit one typed row for each numeric test/report component | Bounded guide prices only; no coverage, provider-cost or cross-jurisdiction equivalence inference |
| Ontario OHIP | 2 June 2026 master-text ZIP, SHA-256 `5beb03539c13bf3d60933fbb46faa18fc3d87cb3741d118d20e427016608cff6` | Extract the fixed-width member; retain service code, effective/termination dates and first positive published fee | The machine-readable member has no descriptors; generated labels identify codes only and must not be read as service descriptions |
| PHARMAC | July 2026 Schedule XML, SHA-256 `313bbcec30028cf84e0554e4a1af940ae24ccba52ef286f8a0749f8f75d39576` | Traverse Chemical/Formulation/Brand/Pack; retain pack ID, names, quantity and published subsidy | CC BY schedule fields with attribution; published subsidy is not represented as confidential rebate or effective net price |

## Academic citation rule

Analyses must cite the provider source and release identifier, not merely the repository. A
reproduction package must cite the repository commit, source-version identifiers, checksums,
parser/transform version and generated output checksum. The software is Apache-2.0; underlying
source data retain their provider-specific terms.

## Field-level lineage

`pixi run field-lineage` generates the checksum-bound field transformation
ledger in `data/derived/field_lineage/`. Each edge records the source dataset
and field, stable transformation identifier, output dataset and field,
content-addressed transformation-code version, input/output SHA-256 digests,
and governing rights-decision identifier.

The native JSONL ledger is authoritative. Deterministic projections are also
provided as W3C PROV-O JSON-LD, RO-Crate 1.2 JSON-LD `CreateAction`
relationships, and OpenLineage 2.0.2 events with a column-lineage dataset
facet. These projections improve interoperability but do not supersede source
payloads, acquisition receipts, rights decisions, or the native ledger.

The first operational slice covers all 17 fields transformed from
`data/seed/source_registry.jsonl` to its CSV mirror by
`scripts/sync_seed_csvs.py`. Further transformations must add records before
their outputs can claim field-level reproducibility.

### Historical backfill and replay

`contracts/medallion/v3/backfill-replay.schema.json` defines the normative
backfill contract. A logical partition is identified by source, archive period,
and logical asset. An immutable snapshot is identified separately by partition,
payload checksum, and metadata checksum. Re-observing the same identity is
idempotent; changed bytes append a new snapshot and an explicit acyclic
`supersedes_snapshot_id` edge rather than overwriting the predecessor.

Late-arriving snapshots replay only their affected partition in canonical
`partition_id`, `correction_sequence`, `snapshot_id` order. Replay plans are
content-addressed from canonical JSON. Missing or failed payloads remain
metadata-only, are excluded from replay, and cannot support evidence claims.
The downloader preserves replaced local bytes under the ignored `.snapshots/`
cache. The committed ledger contains checksums and relative metadata only.

Run `pixi run backfill-replay` to regenerate contracts, the immutable snapshot
ledger, deterministic replay plan, and summary under
`data/derived/historical_sources/backfill_replay/`. The current projection
includes MBS payload receipts and the metadata-only PBS historical catalogue;
it does not claim that PBS historical payloads have been acquired.

### Local CPT enrichment reproduction

Place the official CMS archive at
`data/raw_live/us_cms_pfs/rvu26c-updated-06-30-2026.zip`, verify its SHA-256 against the table
above, then run `pixi run mapping-local-cpt-enrichment`. The command writes the descriptor-bearing
packet to ignored `data/local/mapping_study/cpt_enrichment/` and a descriptor-free summary to
`data/derived/mapping_study/local_cpt_enrichment_summary.json`. The local packet is candidate
evidence only: a new immutable frame, two fresh isolated reviews and accountable adjudication are
required before any case can enter development or holdout evaluation.

## Status boundary

Passing parser, source-contract and data-quality checks demonstrates computational
reproducibility. It does not by itself establish licence approval, clinical validity, research
evidence readiness, OSF registration or publication authorization.

The CMS CLFS release remains intentionally outside automated acquisition because CMS presents the
current archive through an AMA licence gate. The repository may process a manually acquired file
locally, but public outputs must continue to exclude CPT descriptors and retain only fields allowed
by the applicable terms.

## Grouped review matrix

The simple human decisions and their field-level boundaries are generated in
[`LICENCE_DECISION_MATRIX.md`](LICENCE_DECISION_MATRIX.md) and
[`LICENCE_DECISION_MATRIX.json`](LICENCE_DECISION_MATRIX.json). Those files reference
this transformation table, the BPMN process and the checksum-bound review queue. A
group recommendation never changes an individual candidate from `pending`; every final
decision must retain its exact checksum and evidence.
