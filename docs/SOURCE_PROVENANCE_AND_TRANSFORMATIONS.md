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
| MBS current release | July 2026 XML, `au_mbs_20260701_xml` | Parse `Data` records; map `ItemNum`, `Category`, `Group`, `Description`, `FeeStartDate` and `ScheduleFee` to `ScheduleItemRecord`; normalise dates and amounts | Derived approved fields only; raw XML and unrestricted descriptor redistribution excluded |
| MBS historical/full map | July 2026 item-map plus descriptor TXT pair | Parse both files; join on MBS item code; retain joined rows and flag descriptor-only rows | Raw TXT excluded; descriptor-only rows require separate treatment |
| PBS | v3 schedules/items/fees or official CSV fallback | Validate endpoint schemas; join item/fee rows to `/schedules` by `schedule_code`; derive effective date; label prices as schedule/list or payment values | Three PBS derived acquisition artefacts approved; raw payloads, headers and credentials excluded |
| CMS CLFS | Exact manually acquired release | Parse only licence-permitted numeric fields; never redistribute CPT descriptors | Human scope approved; checksum-bound file decision remains required after acquisition |
| CMS PFS | Exact RVU release | Parse numeric RVUs/payment inputs with locality and conversion-factor caveats | Human scope approved; CPT descriptors excluded |
| CMS ASP | Exact July 2026 payment-limit release | Parse payment-limit fields and permitted crosswalk metadata | Human scope approved; no coverage or net-price claims |

## Academic citation rule

Analyses must cite the provider source and release identifier, not merely the repository. A
reproduction package must cite the repository commit, source-version identifiers, checksums,
parser/transform version and generated output checksum. The software is Apache-2.0; underlying
source data retain their provider-specific terms.

## Status boundary

Passing parser, source-contract and data-quality checks demonstrates computational
reproducibility. It does not by itself establish licence approval, clinical validity, research
evidence readiness, OSF registration or publication authorization.
