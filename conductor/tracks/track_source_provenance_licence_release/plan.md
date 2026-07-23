# Implementation plan

- [x] SRC-01: Reconcile historical catalogue targets, retrieval evidence and checksums. (Issue #486, subissue #495)
- [x] SRC-02: Complete source-specific licence and derived-field decision matrices. (Subissue #496)
- [x] SRC-03: Generate BPMN 2.0-compatible transformation lineage for each release family. (Subissue #497)
- [x] SRC-04: Validate source-content and source-contract outputs against the reviewed candidate set. (Subissue #498)
- [x] SRC-05: Produce deterministic citation and package manifests for the frozen cutoff. (Subissue #498)
- [x] SRC-06: Acquire and checksum the licence-free RxNorm Current Prescribable Content monthly
  release as the first medicines counterpart, retaining raw RRF files only in ignored local
  storage. (Issue #490)
- [x] SRC-07: Acquire and checksum final CMS ASP payment-limit and NDC-HCPCS crosswalk releases,
  preserving quarter/version identity and excluding confidential manufacturer data. (Issue #490)
- [x] SRC-08: Add reviewed derived-bundle adapters for RxNorm CPC and CMS ASP with explicit
  source attribution, permitted fields, parser version and deterministic transformation reports.
  (Issue #490)
- [x] SRC-09: Acquire rights-cleared procedure/pathology and genomics counterparts in order:
  CMS CLFS/PFS public fields, LOINC/HPO and NHS Genomic Test Directory. Keep CPT descriptors and
  restricted terminology content local-only. (Issue #490)
- [x] SRC-10: Assess ATC and device terminology redistribution rights; use public openFDA device
  classification metadata and treat restricted ATC,
  GMDN, UMDNS and SNOMED CT content as optional local enrichment rather than a candidate-frame
  prerequisite. (Issue #490)
- [x] SRC-11: Acquire the official July 2026 CMS alpha-numeric HCPCS Level II archive, verify
  SHA-256, and generate a derived-only bundle that excludes numeric CPT and `D`-series dental
  descriptors while recording transformation and licence scope. (Issue #490)
- [x] SRC-12: Add an official RVU26C local-only CPT enrichment adapter. Validate the CMS archive
  member and embedded copyright notice, retain descriptor-bearing candidates only under ignored
  `data/local/`, and publish only release identity, checksums, counts, parameters and restrictions.
  This capability supplies optional evidence for #491; it does not weaken the completed
  rights-cleared acquisition scope in #490. (Issue #490, subissue #491)
- [x] SRC-13: Acquire the complete public openFDA device-classification corpus using deterministic
  pagination, validate total/skip continuity and unique product codes, retain the aggregate payload
  under ignored raw storage, and create a separately versioned reviewed derived bundle. Preserve
  the first-page source version for immutable predecessor cycles. (Issue #490, subissue #491)

Issue #490 is repository-complete for source acquisition: reviewed, checksum-bound RxNorm CPC,
CMS ASP/PFS/HCPCS Level II, HPO and openFDA bundles provide a structurally complete 1,500-case
`expansion_v2` frame. The first frozen review remains immutable and empirically spectrum-blocked;
the expansion must be reviewed as a new cycle under issue #491. Restricted terminology remains
optional local enrichment.

## Validation

- `pixi run historical-sources`
- `pixi run source-validation`
- `pixi run source-contracts`
- `pixi run publication-manifest`
- `pixi run research-package`
- `pixi run public-data-policy`
- `pixi run mapping-candidate-frame`
