# Session: v59 OSF registration snapshot contract

## Implemented

- Hardened the non-mutating OSF registration drift checker for issue #135.
- A remote snapshot must now declare `osf-registration-snapshot-v1`, an OSF
  registration URL, a submission timestamp, `immutable: true`, and a lowercase
  SHA-256 `snapshot_sha256` before fingerprint comparison can produce `ready`.
- Added unit and CLI coverage for incomplete snapshots and documented the
  contract in `docs/OSF_RECONCILIATION.md`.

## Verification

- `pixi run format` passed.
- `pixi run lint` passed.
- `pixi run typecheck` passed.
- OSF and CLI focused tests passed: `19 passed`.

## Boundary

This improves local validation and drift evidence only. It does not create,
submit, approve, amend, embargo, publish or mutate an OSF registration.
