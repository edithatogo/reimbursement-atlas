# Implementation plan

## Dependency order

- [x] GATE-01: Capture the current blocker model from release-readiness, dashboard-review and external-state outputs. The current blocker is `dashboard_human_review` with `displayed_data_parity=false`; Zenodo is published with recorded parity.
- [x] GATE-02: Record the dependency graph and fail-closed publication boundaries in this track, issue drafts and generated Project rows.
- [x] GATE-03: Regenerate the dashboard automated review packet against the current `main` commit and verify displayed values against the generated provenance payloads. (Issue #493)
- [x] GATE-04: Obtain one fresh scoped accountable-owner approval for the exact current packet. The approval names packet hashes, tested commit, routes, browser matrix, provenance scope and exclusions. (Issue #493)
- [ ] GATE-05: Acquire and licence-review the rights-cleared ATC/RxNorm/CMS ASP and other counterpart records; freeze a checksum-bound candidate frame only after #490's source and licence gates pass. (Issue #490)
- [ ] GATE-06: Run blinded adjudication and untouched holdout evaluation only from the frozen counterpart frame; fail closed if quotas, reviewer separation or provenance are incomplete. (Issue #491)
- [ ] GATE-07: Regenerate evidence-readiness, release-readiness, public status, final handoff and publication manifests after GATE-04 and GATE-06. Do not infer evidence readiness from dashboard approval alone.
- [ ] GATE-08: Validate Hugging Face dataset/Space metadata, Croissant, dataset card, source licences and remote identity parity. Keep publication dry-run only while evidence or policy gates are false. (Issue #534)
- [ ] GATE-09: Apply the canonical decision matrix and dependency sequence in `conductor/REMAINING_BLOCKER_CLOSURE_PLAN.md`; record selected option, evidence and contingency for every blocker.
- [x] GATE-10: Preserve any pre-squash local-main commit on a recovery ref, align local `main` to protected `origin/main`, and verify no unrelated work is lost.
- [ ] GATE-11: Verify Zenodo deposition `21759294` read-only and preserve its published receipt; do not mutate the record or reserve a new DOI. (Issue #532)
- [ ] GATE-12: Synchronize OSF metadata only through the approved token-gated workflow after protocol and registration state are eligible; never upload papers or preprints. (Issue #532)
- [ ] GATE-13: Generate the final handoff bundle/archive only after the repository projections and external-state receipts settle.

## Contingencies

- If dashboard packet generation cannot reach current-head parity, retain `dashboard_human_review=blocked`, record the exact mismatch and publish no downstream dataset.
- If counterpart licences or sufficient cases are unavailable, retain #490/#491 as evidence blockers and report the missing source family and quota rather than using fixtures.
- If OSF/Hugging Face credentials or remote services are unavailable, retain a validated dry-run receipt and do not claim submission or publication.
- If any external state changes after regeneration, rerun projections and checksum validation before release or archive actions.

## Validation

- `pixi run dashboard-review-current`
- `conductor/REMAINING_BLOCKER_CLOSURE_PLAN.md`
- `pixi run review-schemas`
- `pixi run release-readiness`
- `pixi run final-handoff`
- `pixi run deterministic-regeneration`
- `pixi run public-data-policy`
