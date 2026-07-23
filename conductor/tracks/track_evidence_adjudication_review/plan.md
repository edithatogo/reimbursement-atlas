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
- [x] EVID-02B: Generate cycle-scoped, checksum-bound blind packets for the separately frozen
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
  `expansion_v9` is the successor evidence cycle. Its 1,500-case frame is frozen at SHA-256
  `1d11079141b1c4e45bbea85f2630c2f16074efce808492bb616af817ca478818`; two isolated
  checksum-bound reviews achieved 81.07% agreement and Cohen's kappa 0.664. Independent
  adjudication proposes 860 positive, 624 negative and 16 excluded cases with zero family-label
  quota gaps. The exact proposal SHA-256
  `dd45a5f8a94d6e050e67c4ee88226104a4e599e8dcd016822e0e9ab7f3830ef5` was approved
  by accountable reviewer `edithatogo` on 2026-07-23. The resulting 1,500 immutable
  adjudication rows are frozen at SHA-256
  `6c30943a871b72cd2ddce637e840d6a1a2a8a6a0fda89658da95414c1495d545`.
  (Subissue #491)
- [x] EVID-02F: Implement the licence-scoped RVU26C local enrichment path for procedure/pathology
  review. Descriptor-bearing hypotheses are ignored local evidence; the tracked summary is
  checksum-bound and descriptor-free. A new immutable study cycle and fresh isolated reviews are
  still required before any additional positives can enter the accountable packet. (Subissue #491)
- [x] EVID-02G: Expand device evidence from the first 1,000 openFDA classifications to the complete
  7,084-record corpus, with deterministic page and payload checksums. Use it only in a new
  immutable study cycle; do not alter predecessor packets or decisions. (Subissue #491)
- [x] EVID-02H: Freeze the dual-tier `expansion_v9` cycle, validate two distinct reviewer-session
  receipts, preserve restricted descriptors only in ignored local evidence, and produce a
  zero-gap checksum-bound adjudication proposal. The accountable owner approved the exact
  proposal hash and the immutable adjudication ledger passes schema validation. (Subissue #491)
- [x] EVID-02C: Make every review, ledger, adjudication, split, threshold, prediction and evaluation
  command cycle-aware so `expansion_v2` cannot overwrite the immutable first study. Reject unsafe
  cycle names and retain backward-compatible initial-cycle paths. (Subissue #491)
- [x] EVID-02D: Correct candidate selection to rank authentic pairs globally after scoring rather
  than pre-sampling left records by hash. Preserve previous cycles and emit new immutable cycles
  whenever candidate-generation semantics change. (Subissue #491)
- [x] EVID-02E: Commit the family-specific mapping codebook and v2 schemas. Include the bounded
  target relation and decision question in blind packets while continuing to hide machine
  hypotheses, scores and split assignment. (Subissue #491)
- [x] EVID-03: Freeze 300 positive/300 negative development cases and an untouched 75 positive/75
  negative holdout only after reference labels are final. The deterministic split is frozen at
  SHA-256 `4387f2405665bf2cae420f82bfa4152efa162331a88ede1c60faeb3effcaeff4`
  with disjoint development and holdout fingerprints. (Subissue #491)
- [x] EVID-03B: Recompute the documented token-Jaccard score from blinded evidence, tune a
  deterministic threshold on development labels only, and freeze checksum-bound holdout
  predictions before evaluating holdout truth. The development-selected threshold is `0.2`,
  development balanced accuracy is `0.895`, and the sealed prediction SHA-256 is
  `95161ce33d9a317b802a91ffe2da592ead086b8c5004033f41cc132673690d49`.
  (Subissue #491)
- [x] EVID-03A: Tune on development only, evaluate the holdout once, and report sensitivity,
  specificity, precision, NPV and balanced accuracy with exact 95% intervals overall and by
  family. The one-time 150-case holdout achieved sensitivity `1.0`, specificity `0.7733`,
  precision `0.8152`, NPV `1.0` and balanced accuracy `0.8867`; all four families met the
  minimum point-estimate criterion. The sealed evaluation is SHA-256
  `d37f4d3ca93f60ac628dfb1ed290887fa06a540298cbf5af157561b5ac80696b`.
  (Subissue #491)
- [x] EVID-04: Complete CMS/MBS/PBS licence-scope review records. (Subissue #492)
- [x] EVID-05: Regenerate the automated dashboard packet against the release candidate commit;
  complete bounded owner visual, keyboard, screen-reader, responsive and provenance review using
  `approved_within_scope`; do not claim universal WCAG conformance. The accountable owner
  approved commit `345576a6f34f3a5ff1d29dd7bca95ebd3abb9f91` against automated packet
  SHA-256 `8bd309e36319971ad2439eefdba6f3a7d175021cd4ef6dc4f2b3ae59aa951523`
  and owner packet SHA-256
  `acac3971909baaa8a85cb3da638b5957cb1d0902edeae39d9f203bcad9af5405`.
  The scope covers 64 automated tests and 44 screenshots across 11 routes and four browser
  projects. Independent manual VoiceOver testing was not performed and no universal
  accessibility-conformance claim is made. (Subissue #493)
- [x] EVID-06: Regenerate evidence-readiness and final-handoff outputs; preserve blockers. (Subissue #494)

## Validation

- `pixi run mapping-calibration`
- `pixi run evidence-readiness`
- `pixi run data-quality`
- `pixi run final-handoff`
- `pixi run dashboard-browser`
- `pixi run review-schemas`
