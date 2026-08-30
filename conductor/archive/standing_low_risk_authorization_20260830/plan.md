# Plan

- [x] Record approved scope and original hashes.
- [x] Implement bounded metadata renewal and delegated dashboard reruns.
- [x] Add regression tests for renewal and fail-closed boundaries.
- [x] Pass all 27 local quality gates; coverage 90.08%; 39 targeted tests pass.
- [x] Complete canonical regeneration and 75 targeted regression tests.
- [x] Route delivery through protected PR #790, which closes #789 only upon merge.

Hosted checks are a separately enforced delivery gate, not a claimed local result.

## Operational follow-up (#791)

- [x] Verify main-run 33295830383 and ingest its passing 64-test, 44-screenshot
  packets without changing the accountable human approval record.
- [x] Remove stale repeat-publication/holdout instructions from completed tasks.
- [x] Document the continuous queue in `docs/AUTONOMOUS_CONTINUATION.md`.
- [x] Diagnose read-only Zenodo run 33296198213 (#792); filter legacy attestation
  aliases, require canonical receipts for every subject, and retain failure diagnostics.
- [x] Regenerate projections and validate: all 27 local quality gates, 39 focused
  tests, standing dashboard scope, 184 approved licence rows and public-data policy.

Delivery remains the protected PR linked from #791. Post-merge read-only Zenodo
verification and its actual outcome are tracked separately on #792; local tests
do not claim remote verification. Neither external gate needs a new owner approval.

Validation follow-up: the first local quality pass found a long line and an
oversized test function; both were corrected. Its sequential coverage process
was superseded after the additional Zenodo fix and terminated, not counted as
passing. The final canonical regeneration/quality pass uses the repository's
supported four-worker work-stealing pytest configuration.

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
