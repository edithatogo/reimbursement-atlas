# Implementation plan

- [x] Record owner permission and implement a common source-level permission gate.
- [x] Replace hard-coded PBS permission blockers in generators; retain publication state.
- [x] Test permission, scope exclusions, malformed/missing/revoked records and acquisition separation.
- [x] Regenerate evidence, reconcile issue/project rows and run quality gates.
- [ ] Deliver through protected CI/PR and archive after verified merge.

Validation: 29 targeted PBS permission, provenance, archive and variant tests pass;
all 27 native local-quality gates pass on the implementation.
Canonical harness regeneration, seed sync, lint/format and public-data policy pass.
External raw transfer is separate work under #255, not an additional owner approval.
