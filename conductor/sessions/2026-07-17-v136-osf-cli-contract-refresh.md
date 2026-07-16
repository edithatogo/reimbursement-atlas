# Session v136: OSF CLI contract refresh

Date: 2026-07-17

## Scope

Verify the repository-pinned `osf-cli-go` toolchain without using OSF credentials or
performing OSF mutation.

## Evidence

- Installed `github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0` into a temporary ignored
  directory.
- `pixi run osf-cli-contract` passed with `OSF CLI contract passed: osf 1.0.0`.
- The unrelated workstation `osf` executable reports `0.3.2` and was not accepted as
  workflow evidence.
- No OSF credentials were read and no project, node, registration, file or metadata was
  changed.

## Outcome

The pinned CLI contract is locally verified. OSF registration and publication remain
fail-closed because the local registration freeze is draft and human methods/licence/
governance approval is absent.
