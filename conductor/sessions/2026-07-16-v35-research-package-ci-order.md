# Conductor session: research-package CI generation order

## Scope

Prevent committed research-package descriptors from lagging behind release-gate hashes produced by
later generation steps.

## Finding

Adding the dashboard accessibility dependency changed the SBOM and therefore the release-readiness
artefact hashes. The descriptors were deterministic but had been generated before the final
release-readiness and seed-lake steps.

## Changes

- Run `pixi run research-package` last in repository automation and data-smoke generation.
- Extend deterministic-regeneration to run release-readiness, seed-lake and research-package in
  that order.
- Refresh the committed Frictionless and RO-Crate descriptors against the final release-gate hashes.

## Acceptance evidence

- The final ordered chain produces no working-tree diff.
- Two consecutive research-package runs are byte-identical.
- The generated-artifact parity gate covers the package step.
