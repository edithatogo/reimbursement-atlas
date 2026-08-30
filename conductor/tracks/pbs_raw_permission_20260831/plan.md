# Implementation plan

- [x] Record owner permission and implement a common source-level permission gate.
- [x] Replace hard-coded PBS permission blockers in generators; retain publication state.
- [x] Test permission, scope exclusions, malformed/missing/revoked records and acquisition separation.
- [ ] Regenerate evidence, reconcile issue/project rows and run quality gates.
- [ ] Deliver through protected CI/PR and archive after verified merge.

Validation: 28 targeted PBS permission, provenance, archive and variant tests pass.
External raw transfer is separate work under #255, not an additional owner approval.
