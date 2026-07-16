# v77 action-pin maintenance automation

## Scope

Implement the remaining local portion of `func_action_sha_pin_bot` under
`track_ci_cd_supply_chain`.

## Implemented

- Added a scheduled/manual GitHub Actions workflow for immutable action-pin maintenance.
- Reused the repository resolver instead of introducing a second SHA-resolution algorithm.
- Refused partial updates when any external action cannot be resolved.
- Preserved trailing version comments while replacing only the exact workflow reference.
- Opened a dedicated normal PR branch and never mutated `main` directly.
- Added focused tests for comment preservation and atomic refusal.
- Regenerated issue drafts, project rows, repository automation, dictionary, dashboard and
  seed-lake outputs.

## Gates

- Ruff formatting and lint pass.
- Focused action-pin tests pass.
- Immutable action policy passes with zero violations.
- Repository automation generation passes.

## Boundary

The implementation is repository-complete after the normal PR and protected-branch checks
pass. Future action updates still depend on network resolution and ordinary maintainer review.
This automation does not authorize source publication, OSF registration, Hugging Face release,
Zenodo deposition or policy claims.
