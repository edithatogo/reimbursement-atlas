# Plan

- [x] Record approved scope and original hashes.
- [x] Implement bounded metadata renewal and delegated dashboard reruns.
- [x] Add regression tests for renewal and fail-closed boundaries.
- [x] Pass all 27 local quality gates; coverage 90.08%; 39 targeted tests pass.
- [x] Complete canonical regeneration and 75 targeted regression tests.
- [x] Route delivery through protected PR #790, which closes #789 only upon merge.

Hosted checks are a separately enforced delivery gate, not a claimed local result.

Validation note: an external SSD disconnect aborted the first quality run with a
bus error. An intermediate type-check failure was corrected, and its superseded
coverage run was terminated. Both gates were rerun through the native gate runner
and passed; the canonical report now records all 27 latest successful results.
No interrupted or failed attempt was treated as a pass.

Hosted review follow-up: bind content-bearing strings (and status-counter names)
to field-specific hashes from the exact 19 approved artifacts. Counters and
SHA-256 fields can renew without approving arbitrary text. Reject duplicate CSV
headers and JSON keys before parsing can discard hidden content. Regression
tests cover hidden fields, local paths, credentials and unapproved payload text.
