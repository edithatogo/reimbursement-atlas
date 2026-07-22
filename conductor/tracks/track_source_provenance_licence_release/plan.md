# Implementation plan

- [x] SRC-01: Reconcile historical catalogue targets, retrieval evidence and checksums. (Issue #486, subissue #495)
- [ ] SRC-02: Complete source-specific licence and derived-field decision matrices. (Subissue #496)
- [x] SRC-03: Generate BPMN 2.0-compatible transformation lineage for each release family. (Subissue #497)
- [x] SRC-04: Validate source-content and source-contract outputs against the reviewed candidate set. (Subissue #498)
- [x] SRC-05: Produce deterministic citation and package manifests for the frozen cutoff. (Subissue #498)

## Validation

- `pixi run historical-sources`
- `pixi run source-validation`
- `pixi run source-contracts`
- `pixi run publication-manifest`
- `pixi run research-package`
- `pixi run public-data-policy`
