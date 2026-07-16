# External quality gates

Initial record: 2026-07-04. Current observation refreshed: 2026-07-17.

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

In the 2026-07-17 build runtime:

- `npm audit --omit=dev --audit-level=moderate` passed.
- `pip-audit --strict` passed with no known vulnerabilities.
- Official Pixi `0.72.2` is available and the Mojo toolchain smoke/parity checks passed.

The earlier DNS-blocked observation remains a historical record in the generated gate
artefacts and ADRs; it must not be carried forward as the current runtime state.

This keeps the repo honest: installed package availability and external advisory reachability are separate facts.
