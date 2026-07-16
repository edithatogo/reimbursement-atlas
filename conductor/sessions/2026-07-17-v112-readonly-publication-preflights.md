# Session v112: read-only publication preflight refresh

## Scope

Refresh current external automation evidence against merged `main` without mutating OSF,
Hugging Face or Zenodo.

## Results

- OSF workflow `29517248071` passed discovery and the pinned component-plan/CLI contract;
  provisioning and publication were skipped.
- Hugging Face workflow `29517250473` passed publication-candidate generation, dashboard
  build and bundle validation; dataset and Space publication were skipped.
- Zenodo workflow `29517252716` passed metadata and repository-readiness validation and
  recorded a non-depositing preflight; no DOI or deposit was created.
- No external project, node, registration, dataset, Space or Zenodo record was mutated.

## Boundary

The runs verify automation and candidate integrity only. Licence review, protocol/methods
approval, evidence readiness, policy-claim review and explicit publication approval remain
required before any write-enabled workflow may run.
