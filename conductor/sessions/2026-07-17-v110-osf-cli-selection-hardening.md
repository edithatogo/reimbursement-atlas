# Session v110: OSF CLI selection hardening

## Scope

Prevent the local OSF contract task from validating an unrelated executable that happens
to appear first on `PATH`, while preserving the repository-pinned `osf-cli-go v1.0.0`
workflow used by CI.

## Implemented evidence

- `scripts/check_osf_cli_contract.py` now requires `--binary` or `OSF_BIN` and refuses
  ambiguous `PATH` lookup.
- The unit contract suite covers both the pinned version check and the refusal path.
- An explicitly installed `github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0` passes the
  unauthenticated, read-only contract.
- The unrelated local `/opt/homebrew/bin/osf` `0.3.2` binary is not accepted or used.
- `docs/OSF_WORKFLOW.md` records the current merged commit and the explicit-selection rule.

## Validation

- Focused OSF contract tests: 3 passed.
- Default `pixi run osf-cli-contract`: fails closed with the explicit-selection message.
- `OSF_BIN=<pinned v1.0.0 binary> pixi run osf-cli-contract`: passed.

## Boundary

This hardens tool selection only. OSF registration, upload and publication remain token-gated
and blocked until protocol, licence, methods and governance review is explicitly approved.
