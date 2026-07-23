# Implementation plan

- [x] EVID-00: Add deterministic, fail-closed mapping pack planning and checksum-bound split contract. (Issue #485, subissue #490)
- [x] EVID-01: Generate the source-stratified 750-case mapping review pack. (Issue #485, subissue #490)
- [x] EVID-01A: Generate and checksum at least 1,500 non-fixture candidate hypotheses with the
  approved 600/400/300/200 family quotas, duplicate-group exclusion and source/period coverage.
  Freeze the frame before review. (Subissue #490)
- [~] EVID-01B: Expand the rights-cleared counterpart spectrum using the official CMS HCPCS
  Level II quarterly archive and other permitted terminology sources. Exclude numeric CPT and
  `D`-series dental descriptors, retain raw archives only under ignored `data/raw_live/`, and
  record source checksums, licence scope and transformations in a reviewed derived bundle.
  The first completed 1,500-case review remains immutable; any expanded frame is a separately
  versioned study cycle. (Subissue #490)
- [x] EVID-02: Generate two isolated, byte-identical blinded packets without hypothesis or split
  disclosure; complete both reviews with evidence citations, confidence and
  exclusion reasons; reviewers cannot see each other or split assignment. Two isolated reviewers
  completed 1,500 cases each; agreement was 894/1,500 and 606 cases require adjudication.
  (Subissue #491)
- [~] EVID-02A: Deterministically adjudicate disagreements and false-positive controls in one
  checksum-bound accountable-owner packet. Independent proposals cover all 1,500 cases, but
  yield only 104 positive and 794 negative includable cases. The packet is therefore
  `blocked_candidate_spectrum` with a 421-case family/label quota gap; owner approval may freeze
  the proposal but cannot waive the approved design. (Subissue #491)
- [ ] EVID-02B: After EVID-01B produces a separately frozen expansion frame, review only the new
  cases with the same blinded-role contract and fill the documented family/label deficits before
  creating development and holdout splits. (Subissue #491)
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
