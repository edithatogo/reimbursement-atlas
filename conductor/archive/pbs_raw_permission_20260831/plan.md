# Implementation plan

- [x] Record owner permission and implement a common source-level permission gate.
- [x] Replace hard-coded PBS permission blockers in generators; retain publication state.
- [x] Test permission, scope exclusions, malformed/missing/revoked records and acquisition separation.
- [x] Regenerate evidence, reconcile issue/project rows and run quality gates.
- [x] Deliver through protected CI/PR and archive after verified merge (PR #801,
  `02116d73da8a8f5dee96009b1ec33691d2704062`).

PR #801 review fixes: validate the complete versioned permission record, explicit
active/non-revoked status and all preservation/exclusion fields. Restrict artefact
approval to schedule publication paths and recognised PDF/structured categories;
do not approve arbitrary same-host resources or use the copyright page as an artefact.
Export the executable model as `schema/PBSRawPermission.schema.json`.

Independent review additionally identified duplicate-key revocation ambiguity and
overbroad keyword matching. Reject duplicate JSON keys before strict validation
and use static complete filename families, not arbitrary keyword matches.
Inventory regression covers 1,048 eligible PDF categories, one excluded format
notice and all 655 structured packages without treating inventory as authority.

Validation: 85 targeted PBS permission, provenance and variant tests pass;
all 27 native local-quality gates pass on the implementation.
Canonical harness regeneration, seed sync, lint/format and public-data policy pass.
External raw transfer is separate work under #255, not an additional owner approval.

Closeout verified 2026-08-31: PR #801 merged at 04:38:08Z with all 25 hosted
checks successful at head `3c54e4e9eb0b612520c64b1b553ad15f9a919b55`.
Head and merge tree both equal `999415853772673847aed633f6e35f118e0e4204`.
The source archive, missing-release evidence and later raw transfer continue in
`conductor/tracks/track_pbs_raw_archive_20260831/`; no raw publication is claimed.
