# Session v86: publication preflight evidence

Date: 2026-07-16

## Scope

Run the repository's read-only OSF discovery, Hugging Face candidate validation and Zenodo
preflight workflows against merged `main`, using the pinned OSF CLI contract and no publication
mutation inputs.

## Evidence

- OSF run `29473382425` succeeded with pinned `osf-cli-go` v1.0.0, found private project `q8cnx`,
  and uploaded only a seven-day sanitized project listing.
- Hugging Face run `29473382378` succeeded; publication candidate manifests and the dashboard
  built and validated, while dataset and Space publication jobs were skipped.
- Zenodo run `29473382399` succeeded with `mutation_performed: false` and `doi_created: false`.
- Local `OSF_BIN=<temporary pinned binary> pixi run osf-cli-contract` passed.

## Boundary

No OSF registration, protocol upload, Hugging Face mutation, Zenodo deposition or DOI creation
occurred. Human protocol/licence/evidence/policy approval remains required before any publication
workflow is run with mutation enabled.
