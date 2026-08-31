# PBS Raw Redistribution Permission

## Active decision (2026-08-31)

The accountable owner stated: "I have permission for raw pbs redistribution",
then directed the project to record and apply it without requiring them to supply
or apply terms. Raw PBS redistribution is allowed on this owner attestation.
No further per-file or checksum approval is required.

The machine-readable record is `data/licence_review/pbs_raw_permission.json`.
Its complete v2 contract is exported as `schema/PBSRawPermission.schema.json`:
all fields are required, status must be active and revocation absent. Truncated,
malformed, duplicate-key or broadened records fail closed without requesting
routine approvals. Duplicate keys cannot conceal a preceding revocation value.
Its basis is `owner_attestation`, not a publisher document independently verified
by the project. No grantor identity, open licence, expiry or new terms are invented.
This decision supersedes the former permission request, retained in Git history.
It must not be sent as a new permission request or treated as an owner blocker.

Scope includes raw PBS schedule PDFs, machine-readable schedule packages,
historical editions and source-identified archive variants, not MBS, CMS or other
sources. Preserve original bytes, copyright notices, attribution, disclaimers,
edition identity, retrieval provenance and checksums. Code remains Apache-2.0;
PBS payloads are not relicensed under Apache-2.0.

Generators now report `allowed_owner_attested_permission` independently from
acquisition and publication. They remain metadata-only: external raw archive
transfer requires a manifest and checksum readback before claiming publication.
Raw payloads remain outside the software Git repository. Missing December 1987
RPBS bytes and early XML/schema recovery remain source gaps, not approval gaps.
Papers and preprints remain excluded.

Artefact eligibility additionally requires a schedule publication path and a
recognised complete filename family for a schedule PDF, amendment or structured
package. Only case and numeric date/version runs are generalized; newly catalogued
filenames do not authorize themselves. Same-host HTML,
copyright pages and unrelated downloads are not approved by hostname alone. The
catalogued `updated-pbs-text-files.pdf` format notice remains metadata-only under
this bounded schedule-artifact contract, not a newly approved schedule payload.

## Remaining source recovery

The current receipts cover 1,048 of 1,049 official historical PDFs and all 655
discovered machine-readable packages. If direct and archive searches cannot
recover the gaps, request these from the PBS publisher:

- The December 1987 RPBS PDF listed at
  `https://www.pbs.gov.au/publication/schedule/1951-2002/1987-12-01-RPBS-Schedule.PDF`.
- December 2006-March 2007 G2B XML releases with their release-specific schema/DTD,
  XSL, version identifiers, amendment history or preservation catalogue references.

This source-recovery request remains prepared, not sent. It is not a request for
another owner licence approval. See [historical boundaries](HISTORICAL_SOURCE_BOUNDARIES.md).
