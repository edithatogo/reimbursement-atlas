# Implementation plan

- [x] EVID-00: Add deterministic, fail-closed mapping pack planning and checksum-bound split contract. (Issue #485, subissue #490)
- [x] EVID-01: Generate the source-stratified 750-case mapping review pack. (Issue #485, subissue #490)
- [x] EVID-01A: Generate and checksum at least 1,500 non-fixture candidate hypotheses with the
  approved 600/400/300/200 family quotas, duplicate-group exclusion and source/period coverage.
  Freeze the frame before review. (Subissue #490)
- [x] EVID-01B: Expand the rights-cleared counterpart spectrum using the official CMS HCPCS
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
- [x] EVID-02A: Deterministically adjudicate disagreements and false-positive controls in one
  checksum-bound accountable-owner packet. Independent proposals cover all 1,500 cases, but
  yield only 104 positive and 794 negative includable cases. The packet is therefore
  `blocked_candidate_spectrum` with a 421-case family/label quota gap; owner approval may freeze
  the proposal but cannot waive the approved design. (Subissue #491)
- [~] EVID-02B: Generate cycle-scoped, checksum-bound blind packets for the separately frozen
  `expansion_v2` frame and complete two fresh isolated reviews without reading the predecessor
  review, other reviewer, hypotheses or split assignment. Then fill the documented family/label
  deficits before creating development and holdout splits. The packet contains 1,500 cases and is
  frozen at SHA-256 `29b357cb20ee2328bb995e733b71075f549703a46f0b62e8a31c0a052a25916c`.
  The first expansion review completed with 93 proposed positives and a 282-positive quota gap.
  A globally ranked second expansion improved this to 130 proposed positives but still lacked an
  explicit family estimand. Both cycles remain immutable diagnostic evidence and are not pooled.
  `expansion_v5` is the first globally ranked, v2-codebook cycle; its 1,500-case packet is frozen
  at SHA-256 `96f9f2465dfe84d65f36172a4d679230dd4a7bbd014407683ccc53d51331041d`
  and fresh isolated reviews plus independent adjudication produced 503 positive, 979 negative and
  18 excluded cases. Procedures, medicines and genomics met their family quotas; devices reached
  45/50 positives. Because no split or holdout was exposed, `expansion_v6` adaptively enriches
  positive hypotheses while preserving every minimum negative quota. No prior decision is
  relabelled or quota-forced.
  The final deduplicated `expansion_v7` cycle contains 1,500 unique duplicate groups and two
  complete isolated reviews. Agreement is 77.47% with Cohen's kappa 0.544. Independent
  adjudication proposes 462 positive, 1,033 negative and five excluded cases, leaving a
  fail-closed 110-positive gap: 83 procedures/pathology and 27 devices. The proposal is
  SHA-256 `7e6e2d1e383dfbd49d4066bb9dbd87a971c0a556ef2ad69a21fb0fc776a986d8`.
  No split or holdout exists. Closing this task requires authoritative positive crosswalks or
  accountable domain adjudication that supplies additional evidence; quotas cannot be waived.
  (Subissue #491)
- [x] EVID-02F: Implement the licence-scoped RVU26C local enrichment path for procedure/pathology
  review. Descriptor-bearing hypotheses are ignored local evidence; the tracked summary is
  checksum-bound and descriptor-free. A new immutable study cycle and fresh isolated reviews are
  still required before any additional positives can enter the accountable packet. (Subissue #491)
- [x] EVID-02G: Expand device evidence from the first 1,000 openFDA classifications to the complete
  7,084-record corpus, with deterministic page and payload checksums. Use it only in a new
  immutable study cycle; do not alter predecessor packets or decisions. (Subissue #491)
- [x] EVID-02C: Make every review, ledger, adjudication, split, threshold, prediction and evaluation
  command cycle-aware so `expansion_v2` cannot overwrite the immutable first study. Reject unsafe
  cycle names and retain backward-compatible initial-cycle paths. (Subissue #491)
- [x] EVID-02D: Correct candidate selection to rank authentic pairs globally after scoring rather
  than pre-sampling left records by hash. Preserve previous cycles and emit new immutable cycles
  whenever candidate-generation semantics change. (Subissue #491)
- [x] EVID-02E: Commit the family-specific mapping codebook and v2 schemas. Include the bounded
  target relation and decision question in blind packets while continuing to hide machine
  hypotheses, scores and split assignment. (Subissue #491)
- [ ] EVID-03: Freeze 300 positive/300 negative development cases and an untouched 75 positive/75
  negative holdout only after reference labels are final. (Subissue #491)
- [ ] EVID-03B: Recompute the documented token-Jaccard score from blinded evidence, tune a
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
