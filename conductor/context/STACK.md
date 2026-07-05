# Stack

## Current design stack

| Layer | Choice |
|---|---|
| Environment | Pixi |
| Build | uv / uv_build |
| Python | 3.14 primary, 3.13 fallback only |
| Validation | Pydantic v2 |
| DataFrames | Polars |
| Interchange/storage | Arrow / Parquet |
| SQL analytics | DuckDB |
| Vector search | LanceDB |
| Graph UI | Cosmograph |
| Dashboard | Astro 7 current-channel |
| Dependency cadence | Latest compatible releases, locked by the repo manifests |
| Type checking | basedpyright strict |
| Lint/format | Ruff strict/all preview-heavy |
| Tests | pytest, Hypothesis, mutmut, smoke/e2e/integration |
| Profiling | Scalene |
| Security | CodeQL, Bandit, pip-audit, dependency review |
| Automation | GitHub Actions, Dependabot, Renovate |

## Mojo

Mojo is reserved for later kernels when there is a clear performance bottleneck:

- high-volume parser tokenisation;
- fuzzy mapping;
- graph edge generation;
- embedding pre-processing;
- probabilistic record linkage.

Do not rewrite stable Python prematurely.
