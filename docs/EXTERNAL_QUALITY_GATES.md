# External quality gates

Date: 2026-07-04

Some quality gates are not purely local. For example, `pip-audit` can be installed locally, but it must reach an external advisory service to resolve vulnerabilities. The repo now records that distinction rather than flattening it into pass/fail.

## Command

```bash
PYTHONPATH=src python scripts/run_external_quality_gates.py
```

Outputs:

- `data/derived/external_quality_gates.json`
- `data/derived/external_quality_gates.csv`
- dashboard copy: `apps/dashboard/public/data/external_quality_gates.csv`

## Outcomes

| Outcome | Meaning |
|---|---|
| `passed` | Gate ran and returned zero. |
| `failed` | Gate ran and found a problem. |
| `blocked_network` | Gate is installed but could not reach a required external service. |
| `missing_tool` | Executable is not present in the runtime. |
| `timed_out` | Gate exceeded the configured timeout. |

## Current runtime observation

In the current build runtime:

- `npm audit --omit=dev --audit-level=moderate` passed.
- `pip-audit --strict` was installed but blocked by DNS resolution to `pypi.org`.
- `pixi` and `mojo` executables were not available on `PATH`; container DNS also blocked installer discovery.

This keeps the repo honest: installed package availability and external advisory reachability are separate facts.
