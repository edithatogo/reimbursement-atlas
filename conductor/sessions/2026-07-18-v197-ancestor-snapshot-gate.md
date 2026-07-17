# v197 ancestor-aware release snapshot gate

## Objective

Keep release-snapshot documentation valid after subsequent protected squash merges without
weakening provenance validation.

## Implementation

- Added shell-free `git merge-base --is-ancestor` validation to the public documentation gate.
- Kept the one-consistent-full-SHA invariant across all five authoritative documents.
- Added a unit test for the fixed argv and ancestor path.
- Updated the REL-001 acceptance criterion and Conductor decision log.

## Evidence

- Public documentation gate: passed.
- Focused public-product tests: 8 passed.
- Ruff and Bandit focused checks: passed.
- No external destination or account setting was mutated.
