# Adjudicate mapping controls and evaluate untouched holdout

Epic: `RAC-EVIDENCE-001` — Evidence adjudication and accountable-review closure

Labels: type:mapping, type:statistics, type:review, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Two fresh isolated reviews cover every checksum-bound expansion_v2 case without hypothesis or split disclosure.
- [ ] Accountable adjudication freezes reference labels before any development or holdout assignment.
- [ ] The deterministic split contains 300 positive and 300 negative development cases plus an untouched 75 positive and 75 negative holdout.
- [ ] Thresholds are tuned on development only; holdout predictions are frozen before truth is evaluated once.
- [ ] Sensitivity, specificity, precision, NPV and balanced accuracy include exact 95 percent intervals overall and by family.
