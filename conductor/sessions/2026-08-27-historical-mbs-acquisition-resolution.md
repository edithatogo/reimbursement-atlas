# Historical MBS acquisition resolution

Date: 2026-08-27

Issue [#255](https://github.com/edithatogo/reimbursement-atlas/issues/255)
remains open only for historical PBS breadth and evidence promotion. The three
previously ambiguous MBS acquisition failures were reconciled against the
official pages:

- `au_mbs_historical_0009` had omitted an official attachment-path segment. The
  corrected HTTPS URL returned 11,865 bytes with SHA-256
  `26ded0e092c786d3031c582766cd2734010793072d224bd63b35f3274b8e541f`.
- `au_mbs_historical_0004` and `au_mbs_historical_0005` return official HTTP 404
  responses and are no longer linked from the current downloads page or the
  July 2026 release page. They are recorded as `upstream_unavailable`, not as
  retryable network failures and not as acquired evidence.

The resulting bounded state is 341 acquired/checksum-bound targets and two
metadata-only unavailable targets. Raw bytes remain in ignored local storage;
download does not grant redistribution rights. Historical PBS remains
metadata-only because the official rolling API is not a complete archive. No
source-completeness, redistribution, research, paper or preprint claim follows
from this reconciliation.
