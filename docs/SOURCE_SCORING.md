# Source Readiness Scoring

The source score is a transparent access/readiness rubric, not a measure of
clinical validity, evidence quality, or licence status. The canonical grade
cutoffs are defined in `reimburse_atlas.scoring` and are used by the generated
readiness tables.

`grade_sensitivity` evaluates alternative `(A, B, C)` cutoffs against the same
scores without changing the canonical rubric. Use it for robustness reporting
when a conclusion depends on a grade boundary. Alternative thresholds must be
strictly ordered (`A > B > C >= 0`), and the output is a count table rather than
a replacement source grade.
