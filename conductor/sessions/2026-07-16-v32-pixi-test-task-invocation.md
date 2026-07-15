# Conductor session: Pixi test task invocation

## Scope

Make the local and CI test task entrypoints robust to relocatable Pixi environments.

## Evidence

- The official Pixi environment's `pytest` script had a shebang pointing to a deleted temporary
  checkout, causing `pixi run unit` to fail with `No such file or directory`.
- `python -m pytest` used the active Pixi interpreter and passed all five test lanes:
  - unit: 218 passed
  - smoke: 4 passed
  - property: 1 passed
  - integration: 1 passed
  - end-to-end: 9 passed

## Changes

- Updated the Pixi `unit`, `smoke`, `property`, `integration`, `e2e`, `test` and `coverage` tasks
  to use `python -m pytest`.
- Added issue #192 and placed it on Project #18.
- Regenerated issue drafts, Project exports, dashboard mirrors, seed lake and release evidence.

## Decision

Keep the module invocation as the canonical task form; it is tied to the active environment and does
not depend on a relocatable console-script shebang.
