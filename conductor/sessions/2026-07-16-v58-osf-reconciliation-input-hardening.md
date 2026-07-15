# Session: v58 OSF reconciliation input hardening

## Implemented

- Added fail-closed validation for generated OSF sync-manifest rows and exported
  remote-state rows before reconciliation.
- Rejected duplicate manifest IDs and local/remote OSF paths, path traversal,
  absolute local paths, negative sizes and malformed SHA-256 values.
- Added unit and CLI end-to-end coverage for unsafe, duplicate and malformed
  inputs without performing network IO or remote mutation.
- Documented the validation contract in `docs/OSF_RECONCILIATION.md`.

## Verification

- `pixi run format-check` passed.
- `pixi run lint` passed.
- OSF sync and CLI end-to-end tests passed: `18 passed`.

## Boundary

This closes the repository-owned input-safety portion of issue #134. A real
`osf-cli-go` mutation adapter, credentialed remote snapshot and human publication
approval remain intentionally external and fail-closed.
