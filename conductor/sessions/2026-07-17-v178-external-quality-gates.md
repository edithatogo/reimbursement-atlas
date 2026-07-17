# Conductor session: v178 external quality gates

Date: 2026-07-17

## Results

`pixi run external-quality-gates` passed:

- strict `pip-audit`
- dashboard `npm audit --omit=dev --audit-level=moderate`
- official Pixi availability and installer reachability
- zizmor workflow security analysis
- repository automation matrix
- Mojo availability via `uv tool run --from mojo-compiler mojo --version`

## Outputs

- `data/derived/external_quality_gates.json`
- `data/derived/external_quality_gates.csv`

The reports contain redacted command evidence and no secrets or raw source payloads. This gate
refresh does not change the fail-closed research, evidence, licence, policy or publication status.
