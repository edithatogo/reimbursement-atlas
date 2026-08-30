# Plan

- [x] Recheck December 1987 PDF endpoints and official legacy XML evidence. (`e2227370`)
- [x] Record the precise acquisition/schema gaps and update the publisher request. (`e2227370`)
- [x] Validate, review and archive bounded repository investigation; delivery in PR #795.

Issue #255 must remain open for unavailable source bytes and raw redistribution
rights. Completing this investigation does not satisfy those external gates.

## Review

Official HTTP responses, bounded CDX filters and published schema documentation
are distinguished from payload bytes and release-specific parser contracts.
The mobile-host search hit is explicitly rejected as acquisition evidence.
No data payload, new approval or external communication was produced.

Validation: all 27 native local-quality gates passed using four pytest workers;
the public-data policy, Python 3.14, coverage, type, security and dashboard build
gates are included. Track links/metadata validate. Issue/Project, dictionary and
roadmap projections were regenerated. Hosted protected checks remain required
for the final archive commit before merge. The implementation head `f7cc057b`
passed all 24 hosted checks before the subsequent review fixes below.

## Review fixes

- [x] Distinguish failed locators from previously acquired TXT identities using
  checksum-bound snapshot reconciliation; preserve original transfer receipts.
- [x] Project the December 2006-March 2007 XML/schema gap into generated issues.
- [x] Validate reconciliation regressions and regenerate projections: all 27
  native local-quality gates pass; twelve targeted reconciliation/projection
  tests pass. The initial architecture assignment failure was fixed, not waived.
- [x] Require source, filename and URL equality for direct receipts so reused
  target IDs cannot establish acquisition evidence for a different source file.
- [x] Pass exact-head hosted checks before protected merge: all 24 checks on
  `6ba660f1cdad4e150f47b006971c9f471df2d229`; PR #795 merged as
  `f82c47b82346d1fa4927d0dcdc8983aadf2f346c`. Merged and tested trees match.
