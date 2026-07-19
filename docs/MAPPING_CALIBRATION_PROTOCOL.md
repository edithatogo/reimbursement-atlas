# Mapping Calibration Protocol

Status: owner-approved protocol; evidence gate remains review-required.

## Estimands

The primary estimands are recall and specificity for the declared mapping task.
Precision is reported secondarily. The four-case fixture is a smoke test only and
must not be used as an evidence estimate.

## Design

- Development set: 300 positive and 300 negative cases.
- Untouched holdout: 75 positive and 75 negative cases.
- Total planned cases: 750.
- Cases must be independent at the evaluated entity level; repeated codes or
  near-duplicate records are grouped and assigned to one split.
- Sampling is stratified by source jurisdiction, coding system, clinical/domain
  area, difficulty and decision-relevant scope.
- The mapping threshold, inclusion/exclusion rules and acceptable performance
  thresholds are fixed before evaluation.

## Review and adjudication

Two qualified reviewers independently assess each case while blinded to the
machine candidate score and the other reviewer's decision. Disagreements are
referred to a qualified third reviewer for adjudication. Reviewer roles,
qualification, timestamps, rationale and adjudication outcomes are recorded
against the case identifier without storing restricted source text.

## Release boundary

The development set may support threshold tuning. The holdout is not inspected
for tuning and is evaluated once the protocol is frozen. Results remain
`review_required` until the case pack, reviewer records, adjudication summary
and holdout report are present. Protocol approval does not approve a mapping,
clinical equivalence, policy claim or publication.

The reproducible planning calculation is in
`data/derived/vertical_slice/mapping_power_calculation.json` and `.md`. Its
assumptions must be re-estimated if the estimand, class balance, clustering,
case spectrum or adjudication process changes.
