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
| CMS CLFS | Exact manually acquired release | Parse only licence-permitted numeric fields; never redistribute CPT descriptors | Candidate scope is defined; checksum-bound field decision remains required after acquisition |
| CMS PFS | RVU26C July 2026 archive, SHA-256 `d45a158e02694c1539e7f88192c611883e377181eda86dc213359707bcacbacb` | Validate the expected `PPRRVU2026_Jul_nonQPP.csv` member and embedded AMA notice; parse numeric RVUs/payment inputs; optionally rank MBS-to-CPT hypotheses using descriptor text only in ignored local storage | Public outputs contain release identity, checksums, counts, parameters and restrictions only; CPT descriptors and descriptor-bearing candidates are never committed or published |
| CMS ASP | Exact July 2026 payment-limit release | Parse payment-limit fields and permitted crosswalk metadata | Candidate payment fields only; no coverage or net-price claims pending source review |

## Academic citation rule

Analyses must cite the provider source and release identifier, not merely the repository. A
reproduction package must cite the repository commit, source-version identifiers, checksums,
parser/transform version and generated output checksum. The software is Apache-2.0; underlying
source data retain their provider-specific terms.

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

## Grouped review matrix

The simple human decisions and their field-level boundaries are generated in
[`LICENCE_DECISION_MATRIX.md`](LICENCE_DECISION_MATRIX.md) and
[`LICENCE_DECISION_MATRIX.json`](LICENCE_DECISION_MATRIX.json). Those files reference
this transformation table, the BPMN process and the checksum-bound review queue. A
group recommendation never changes an individual candidate from `pending`; every final
decision must retain its exact checksum and evidence.
