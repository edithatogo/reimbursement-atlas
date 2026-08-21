# Implementation Plan

## Phase 1: Readiness and prerequisites

- [x] Confirm scope, rights, licensing, metadata, release, and persistence prerequisites in the parent issue.
- [x] Capture repository-specific validation commands and baseline results.
- [x] Add the repository-side registry readiness contract and regression assertion.

## Phase 2: Registry deliverables

- [x] [Issue #531](https://github.com/edithatogo/reimbursement-atlas/issues/531) — checksum-bound licensing and release metadata validated.
- [x] [Issue #532](https://github.com/edithatogo/reimbursement-atlas/issues/532) — repository-side
  metadata, exact-tag inventory, attestation and remote-parity automation are implemented. Zenodo
  deposition `21759294` is published as DOI `10.5281/zenodo.21759294`; all 12 files and metadata
  pass recorded remote parity. OSF is retained only as historical evidence after destination
  deprecation.
- [x] [Issue #533](https://github.com/edithatogo/reimbursement-atlas/issues/533) — eligibility assessed and submission deferred until searchable-service maturity.
- [x] [Issue #534](https://github.com/edithatogo/reimbursement-atlas/issues/534) — Croissant and remote Hugging Face identity/licence parity validated.

## Phase 3: Reconciliation and closeout

- [x] Reconcile Conductor status, issue state, project state, and external evidence.
- [x] Run the repository's documented validation workflow (`pytest tests/test_registry_readiness_contract.py`, `pixi run project-issues`, `pixi run github-project-export`, `pixi run docs-freshness`, `pixi run public-data-policy`, `pixi run lint`, `pixi run format-check`, and `pixi run typecheck`).
- [x] Archive this track after all automatable work is complete and every remaining external gate is explicit.
- [x] Review fix: declare the evidence ledger schema in track metadata.

Zenodo publication and remote parity now have authoritative external evidence.
FAIRsharing remains deliberately deferred by the searchable-service maturity
assessment and is outside this track's completed acceptance criteria.
