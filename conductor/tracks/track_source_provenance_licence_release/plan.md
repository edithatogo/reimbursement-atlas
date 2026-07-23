# Implementation plan

- [x] SRC-01: Reconcile historical catalogue targets, retrieval evidence and checksums. (Issue #486, subissue #495)
- [x] SRC-02: Complete source-specific licence and derived-field decision matrices. (Subissue #496)
- [x] SRC-03: Generate BPMN 2.0-compatible transformation lineage for each release family. (Subissue #497)
- [x] SRC-04: Validate source-content and source-contract outputs against the reviewed candidate set. (Subissue #498)
- [x] SRC-05: Produce deterministic citation and package manifests for the frozen cutoff. (Subissue #498)
- [~] SRC-06: Acquire and checksum the licence-free RxNorm Current Prescribable Content monthly
  release as the first medicines counterpart, retaining raw RRF files only in ignored local
  storage. (Issue #490)
- [ ] SRC-07: Acquire and checksum final CMS ASP payment-limit and NDC-HCPCS crosswalk releases,
  preserving quarter/version identity and excluding confidential manufacturer data. (Issue #490)
- [ ] SRC-08: Add reviewed derived-bundle adapters for RxNorm CPC and CMS ASP with explicit
  source attribution, permitted fields, parser version and deterministic transformation reports.
  (Issue #490)
- [ ] SRC-09: Acquire rights-cleared procedure/pathology and genomics counterparts in order:
  CMS CLFS/PFS public fields, LOINC/HPO and NHS Genomic Test Directory. Keep CPT descriptors and
  restricted terminology content local-only. (Issue #490)
- [ ] SRC-10: Assess ATC and device terminology redistribution rights; treat restricted ATC,
  GMDN, UMDNS and SNOMED CT content as optional local enrichment rather than a candidate-frame
  prerequisite. (Issue #490)

## Validation

- `pixi run historical-sources`
- `pixi run source-validation`
- `pixi run source-contracts`
- `pixi run publication-manifest`
- `pixi run research-package`
- `pixi run public-data-policy`
- `pixi run mapping-candidate-frame`
