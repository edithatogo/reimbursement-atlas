# v169 current-main preflight convergence

Date: 2026-07-17
Track: `track_live_source_ingestion`, `track_research_protocols_osf`, `track_publication_hf_spaces`, `track_ci_cd_supply_chain`, `track_public_product_citation_dashboard`

## Scope

Refresh current external evidence after merged commit `e46a629` without performing
publication, provisioning, deposit or destination metadata mutation.

## Evidence

- OSF run [29571893420](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571893420) passed the pinned `osf-cli-go v1.0.0` plan and discovery. It found 28 accessible projects, including private project `q8cnx`; provisioning, registration, upload and publication were skipped.
- Zenodo run [29571894944](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571894944) passed non-depositing validation with `mutation_performed: false` and `doi_created: false`.
- Credentialed source-health run [29571899135](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571899135) passed and schema-validated 14,867 PBS records. Six remaining targets require licence review and raw payloads stayed runner/local-only.
- Hugging Face destination run [29571896396](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571896396) failed closed on the known Space drift (`mit`/`gradio` versus `apache-2.0`/`static`) and performed no mutation.
- GitHub security settings run [29571897692](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571897692) completed with a redacted `blocked_permissions` monitor result. The authenticated repository API readback remains the source of truth for current repository controls.

## Outcome

Documentation was updated, validated and merged in PR #419. The repository remains software-release-ready, but research publication, evidence release, OSF registration, policy claims and HF Space reconciliation remain fail-closed. The 161-row licence queue remains pending with zero approvals.

## Next boundary

Continue with reviewer-ready packets, mapping adjudication and cross-platform visual review. Do not publish to OSF, Hugging Face or Zenodo, and do not mutate governed metadata, until the corresponding human and licence gates are explicitly approved.
