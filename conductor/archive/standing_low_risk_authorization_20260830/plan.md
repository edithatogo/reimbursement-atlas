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

Review fixes for PR #793: completed Hugging Face tasks dispatch the actual
destination-metadata workflow. Completed Zenodo tasks dispatch `mode=verify` with
the recorded deposition ID and release tag; missing or malformed identity yields
an explicit recovery instruction, never an invented target or publication call.
Regression tests cover valid release identities, missing metadata and shell-like
tag content. Local planning is not represented as remote verification.

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

Operational renewal exposed a circular source-drift checksum receipt: hosted
packets used the current receipt while validation borrowed the historical human
snapshot. Exclude this derived checksum-of-checksums consistently; underlying
public datasets remain fingerprinted and source-drift gates remain enforced.
Regression coverage verifies shallow/history-independent renewal and rejection
of changed underlying source content. No new accountable approval is required.
All 27 local quality gates passed with four workers after this fix. The broad
regenerator also launched a duplicate serial quality run; that redundant run was
terminated, not counted as passing, and regeneration resumed after the already
completed quality step. Hosted checks still validate the final exact tree.
Platinum promotion statuses also depend on dashboard readiness. Normalize only
known machine-generated status/gate/reason values for Platinum rows, retaining
all source identities, checksums, rights, required gates and scope text. Unknown
payload text and non-Platinum status changes still invalidate the fingerprint.

Issue #792 post-merge verification run 33300908624 passed inventory loading,
remote file checksums and Zenodo metadata parity, then exposed a DOI resolver
bug: the HTML landing page was parsed as JSON. Resolve DOI redirects without
reading JSON, while keeping DataCite JSON parsing strict. Regression tests
verify credential-free requests, HTML DOI resolution and rejection of HTML at
the registry JSON endpoint. Retry read-only verification after protected merge;
the historical publication receipt is preserved and no publication is repeated.
