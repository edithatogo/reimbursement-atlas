# Session v38: Python 3.14 local validation

## Scope

Refresh runtime evidence after the environment gained current Python 3.14 and official Pixi support.

## Evidence

- `pixi run python --version`: Python 3.14.6.
- `uv run --python 3.14 python --version`: Python 3.14.5.
- `pixi run test`: 233 tests passed.
- `bash scripts/run_mojo_smoke.sh`: passed.
- `uv tool run --from mojo-compiler mojo --version`: Mojo 0.26.2.0.
- External quality records pass for pip-audit, npm audit, official Pixi, Pixi installer reachability,
  zizmor, repository automation and Mojo.

## Decision

Python 3.14 is now the active local and CI validation target. Python 3.13 remains a compatibility
fallback only where Python 3.14 cannot be installed.
