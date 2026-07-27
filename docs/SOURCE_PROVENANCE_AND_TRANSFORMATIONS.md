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
