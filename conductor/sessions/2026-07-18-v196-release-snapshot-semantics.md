# v196 release-snapshot semantics

## Objective

Prevent protected squash merges from making authoritative handoff headers claim that a prior
documentation commit is still the live `main` tip.

## Decision

Use release-snapshot wording for the recorded SHA and explicitly state that the checkout may be
newer. Preserve the full SHA invariant and the historical monitor boundary.

## Validation

- `scripts/check_public_docs.py` passes with a consistent snapshot SHA.
- The release-readiness matrix remains 36/36 passing for repository gates.
- No external monitor or publication destination was mutated.
