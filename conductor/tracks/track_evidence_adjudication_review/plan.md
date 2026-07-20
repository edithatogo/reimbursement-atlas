# Implementation plan

- [ ] EVID-01: Generate the source-stratified 750-case mapping review pack. (Issue #485, subissue #490)
- [ ] EVID-02: Complete blinded dual review and adjudication of positive/negative controls. (Subissue #491)
- [ ] EVID-03: Evaluate the untouched holdout and calculate uncertainty intervals. (Subissue #491)
- [ ] EVID-04: Complete CMS/MBS/PBS licence-scope review records. (Subissue #492)
- [ ] EVID-05: Complete dashboard visual/accessibility review within stated scope. (Subissue #493)
- [ ] EVID-06: Regenerate evidence-readiness and final-handoff outputs; preserve blockers. (Subissue #494)

## Validation

- `pixi run mapping-calibration`
- `pixi run evidence-readiness`
- `pixi run data-quality`
- `pixi run final-handoff`
- `pixi run dashboard-browser`
