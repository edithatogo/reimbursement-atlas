# Human-in-the-loop mapping workbench

## Scope

Provide a checksum-bound mapping candidate frame, isolated blinded review
packets, deterministic adjudication and one-time development/holdout
evaluation for permitted derived records. Candidate labels remain hypotheses
until accountable adjudication is complete.

## Acceptance criteria

- Candidate frames are generated from permitted derived records and carry
  source/version/checksum provenance.
- Reviewer packets are role-isolated and do not disclose split assignment or
  the other reviewer's decisions.
- Adjudication fails closed until complete, checksum-bound accountable review is
  supplied.
- Development and untouched holdout splits are disjoint and deterministic;
  holdout metrics are evaluated once with exact intervals.
- No broad atlas-performance or evidence-readiness claim is made while the
  accountable adjudication gate remains incomplete.
