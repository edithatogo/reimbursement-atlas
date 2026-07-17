# Session v152: Pixi task boundary

## Objective

Make the documented Python security and build commands executable through the official Pixi
environment without duplicating or weakening the uv-managed project dependency boundary.

## Changes

- Routed `bandit` and `pip-audit` Pixi tasks through `uv run --all-extras`.
- Added a `pixi run build` alias for `uv build`.
- Updated local toolchain documentation and README commands.
- Added a unit contract test for the three task definitions.
- Added the implementation to the CI/security Conductor backlog.

## Validation boundary

The three aliases and focused contract test pass locally. Network advisory results, source-data
licence decisions and external publication gates remain separate from this toolchain change.
