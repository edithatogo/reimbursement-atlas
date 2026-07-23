# Adjudicate mapping controls and evaluate untouched holdout

Epic: `RAC-EVIDENCE-001` — Evidence adjudication and accountable-review closure

Labels: type:mapping, type:statistics, type:review, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Two fresh isolated reviews cover every case in the current checksum-bound, codebook-defined expansion cycle without hypothesis, candidate-score or split disclosure.
- [x] Accountable adjudication freezes reference labels before any development or holdout assignment.
- [x] The deterministic split contains 300 positive and 300 negative development cases plus an untouched 75 positive and 75 negative holdout.
- [x] Thresholds are tuned on development only; holdout predictions are frozen before truth is evaluated once.
- [x] Sensitivity, specificity, precision, NPV and balanced accuracy include exact 95 percent intervals overall and by family.
- [x] Any material source, mapping-rule, model or threshold change creates a new immutable cycle and untouched holdout; the evaluated holdout is never retuned or pooled.
