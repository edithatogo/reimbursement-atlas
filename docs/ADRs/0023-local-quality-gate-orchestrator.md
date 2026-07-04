# ADR 0023: Local quality-gate orchestrator

## Status

Accepted.

## Context

The repository has intentionally ambitious quality requirements: Ruff, strict basedpyright, coverage thresholds, seed-data sync, public-data governance, dashboard build, SBOM generation, repository automation checks and supply-chain/security gates. Running these as isolated commands makes it harder for future agents to know what was actually executed and what was blocked by the environment.

## Decision

Add a first-class local quality-gate orchestrator in `src/reimburse_atlas/local_quality.py` with a script entry point at `scripts/run_local_quality_gates.py`. The orchestrator records every command, status, duration, excerpts, blocking/advisory classification and run summary.

Profiles are split into `quick`, `ci`, `release` and `nightly` so long-running or network-backed gates do not silently destabilise PR workflows.

## Consequences

- CI can upload a single evidence bundle for local-quality parity.
- Conductor sessions can cite structured validation artefacts instead of prose-only status updates.
- Network/tool availability is represented honestly as `blocked_network`, `missing_tool`, `wrong_tool` or `timed_out`.
- The repo now has both Pixi and uv CI paths.
