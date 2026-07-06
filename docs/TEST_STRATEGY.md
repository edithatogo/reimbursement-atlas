# Test strategy

## Test pyramid

| Layer | Purpose | Examples |
|---|---|---|
| Unit | Fast validation of models, parsers and quality helpers. | Pydantic validation, checksum, duplicate id detection. |
| Property | Invariant testing with Hypothesis. | Stable ids, reversible normalization, parser row-count invariants. |
| Integration | Data engines and local marts. | Polars -> Arrow -> DuckDB round trips. |
| End-to-end | User workflows. | CLI validate, ingest fixture, export graph. |
| Smoke | Repository health. | Required files, seed data present, dashboard build. |
| Mutation | Test quality. | mutmut over core models/parsers. |

## Coverage target

- Minimum: 90%.
- Aspirational: 95% for core models, parsers, validators and mappers.
- Coverage is not enough: mutation score should be introduced after first parser slice.

## CI matrix

- Python 3.14 primary runtime target in CI.
- Python 3.13 remains a local sandbox fallback only when 3.14 cannot be installed.
- Linux primary.
- macOS optional for Mojo/Pixi if GitHub Actions minutes permit.
- Dashboard Node build.
- Security scan jobs.
- Nightly mutation and dependency update jobs.

## Test-goblin compatibility profile

The `test-goblin` extra is now a practical compatibility profile rather than a dependency on a single unresolved package. It installs Hypothesis, mutmut and pytest-randomly to support goblin-style generative, mutation and order-sensitivity testing. See `docs/TEST_GOBLIN_COMPATIBILITY.md`.

## v6 local validation target

The Python core should pass Ruff, Ruff format check, basedpyright, Bandit, compileall, `uv build` and a pytest coverage gate of at least 90% over the core package. Optional CLI/API/MCP/warehouse shells remain smoke-tested and are excluded from the coverage denominator until they become production surfaces.


## v7 mutation and dashboard smoke updates

Dashboard reproducibility is now smoke-tested by requiring `apps/dashboard/package-lock.json`, dashboard entrypoints and key dashboard-safe CSV assets to exist. The full Node gate remains `npm ci && npm run build`.

Pytest now sets `pythonpath = ["src"]`, which allows mutmut to import mutated source paths correctly. Full mutmut is configured and was proven to generate mutants, collect stats, run clean tests and start mutant evaluation, but it remains a scheduled/manual gate because the current configuration generated 3,673 mutants across 45 files.
