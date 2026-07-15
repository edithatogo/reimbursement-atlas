# Session v28: OSF CLI contract hardening

Date: 2026-07-16

## Scope

- Verify the stable `osf-cli-go v1.0.0` release and its command surface.
- Add a local/CI contract check that does not read credentials or make network requests.
- Keep OSF reconciliation, registration and publication fail-closed.
- Regenerate research-package metadata and cross-reference the Conductor backlog.

## Evidence

- `/tmp/osf-v1/osf --version` returned `1.0.0`.
- `scripts/check_osf_cli_contract.py` passed against the v1.0.0 binary.
- Focused OSF tests passed: 10 tests.
- Ruff and basedpyright passed for the new script and tests.
- Public-data policy passed.

## Boundary

This verifies the local toolchain contract only. It does not authenticate to OSF, create or
modify projects, upload files, submit registrations, or change any `publish_allowed` value.
