# Implementation plan

- [x] EVID-00: Add deterministic, fail-closed mapping pack planning and checksum-bound split contract. (Issue #485, subissue #490)
- [x] EVID-01: Generate the source-stratified 750-case mapping review pack. (Issue #485, subissue #490)
- [x] EVID-01A: Generate and checksum at least 1,500 non-fixture candidate hypotheses with the
  approved 600/400/300/200 family quotas, duplicate-group exclusion and source/period coverage.
  Freeze the frame before review. (Subissue #490)
- [~] EVID-02: Generate two isolated, byte-identical blinded packets without hypothesis or split
  disclosure; complete both reviews with evidence citations, confidence and
  exclusion reasons; reviewers cannot see each other or split assignment. (Subissue #491)
- [ ] EVID-02A: Deterministically adjudicate disagreements and false-positive controls in one
  checksum-bound accountable-owner packet. (Subissue #491)
- [ ] EVID-03: Freeze 300 positive/300 negative development cases and an untouched 75 positive/75
  negative holdout only after reference labels are final. (Subissue #491)
- [~] EVID-03B: Recompute the documented token-Jaccard score from blinded evidence, tune a
  deterministic threshold on development labels only, and freeze checksum-bound holdout
  predictions before evaluating holdout truth. (Subissue #491)
- [ ] EVID-03A: Tune on development only, evaluate the holdout once, and report sensitivity,
  specificity, precision, NPV and balanced accuracy with exact 95% intervals overall and by
  family. (Subissue #491)
- [x] EVID-04: Complete CMS/MBS/PBS licence-scope review records. (Subissue #492)
- [~] EVID-05: Regenerate the automated dashboard packet against the release candidate commit;
  complete bounded owner visual, keyboard, screen-reader, responsive and provenance review using
  `approved_within_scope`; do not claim universal WCAG conformance. (Subissue #493)
- [x] EVID-06: Regenerate evidence-readiness and final-handoff outputs; preserve blockers. (Subissue #494)

## Validation

- `pixi run mapping-calibration`
- `pixi run evidence-readiness`
- `pixi run data-quality`
- `pixi run final-handoff`
- `pixi run dashboard-browser`
- `pixi run review-schemas`
