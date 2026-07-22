# Implementation plan

- [x] REL-01: Reconcile README, CITATION.cff, dashboard status and package identity. (Issue #487, subissue #499)
- [x] REL-01A: Add a structured human dashboard visual/accessibility/provenance review record contract. (Issue #487, subissue #501)
- [ ] REL-02: Complete scoped visual/accessibility and provenance review evidence. (Subissue #501)
- [x] REL-03: Validate OSF/HF/GitHub identity, metadata and licence-boundary parity. (Subissue #503)
- [x] REL-04: Generate reproducible archive, SBOM, provenance and attestation inputs. (Subissue #505)
- [ ] REL-05: Run final release-readiness and publication boundary review; do not publish papers. (Subissue #507)

## Validation

- `pixi run citation-validate`
- `pixi run dashboard-quality`
- `pixi run dashboard-routes`
- `pixi run release-readiness`
- `pixi run final-handoff`
- `pixi run public-data-policy`
