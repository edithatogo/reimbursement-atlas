# Layered harness engineering and deterministic regeneration

## Scope

Run bounded unit, property, integration, end-to-end, mutation and
deterministic-regeneration harnesses with auditable failure evidence and
separate hosted lanes.

## Acceptance criteria

- Property, integration and end-to-end harnesses run as separate lanes with
  bounded resource use.
- Generated outputs are regenerated and checked for a clean diff.
- Mutation testing is bounded by timeout/cancellation controls.
- Test, coverage and harness contracts are reproducible locally where tools are
  available.
- Experimental TypeScript upgrades remain blocked until the Astro checker peer
  contract is compatible and the canary passes.
