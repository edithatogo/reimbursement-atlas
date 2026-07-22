# Implementation Plan

## Phase 1: Readiness and prerequisites

- [x] Confirm scope, rights, licensing, metadata, release, and persistence prerequisites in the parent issue.
- [x] Capture repository-specific validation commands and baseline results.
- [x] Add the repository-side registry readiness contract and regression assertion.

## Phase 2: Registry deliverables

- [ ] [Issue #531](https://github.com/edithatogo/reimbursement-atlas/issues/531)
- [ ] [Issue #532](https://github.com/edithatogo/reimbursement-atlas/issues/532)
- [ ] [Issue #533](https://github.com/edithatogo/reimbursement-atlas/issues/533)
- [ ] [Issue #534](https://github.com/edithatogo/reimbursement-atlas/issues/534)

## Phase 3: Reconciliation and closeout

- [x] Reconcile Conductor status, issue state, project state, and external evidence.
- [x] Run the repository's documented validation workflow (`pytest tests/test_registry_readiness_contract.py`, `pixi run project-issues`, `pixi run github-project-export`, `pixi run docs-freshness`, `pixi run public-data-policy`, `pixi run lint`, `pixi run format-check`, and `pixi run typecheck`).
- [ ] Archive this track only after all automatable work is complete and every remaining external gate is explicit.

The remaining Phase 2 rows are intentionally open: licensing metadata, DOI
deposition, FAIRsharing eligibility, and Hugging Face publication require
external account, rights, or publication decisions. The repository-side
contract is complete and fail-closed; no external registry mutation is implied.
