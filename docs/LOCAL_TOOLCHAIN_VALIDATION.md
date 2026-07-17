# Local toolchain validation

The v6 development pass converts the toolchain from mostly scaffolded to locally exercised for the Python core. The repository now has a practical "installed toolchain" path using `uv` and the project extras.

## Bootstrap

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e '.[dev,api,mcp,test-goblin]'
```

The `test-goblin` extra is a compatibility profile rather than a dependency on a single package. It installs the components currently used for goblin-style generative and adversarial testing: Hypothesis, pytest-randomly and mutmut.

## Core quality gate

```bash
pixi run lint
pixi run format-check
pixi run typecheck
pixi run coverage
pixi run bandit
python -m compileall -q src scripts tests
pixi run build
```

## Coverage policy

Coverage is enforced at 90% over the core library. Read-only interface shells and optional runtime surfaces are smoke-tested but excluded from the coverage denominator until they become production surfaces:

- `api.py`
- `cli.py`
- `mcp_server.py`
- `parsers/base.py`
- `warehouse.py`

This prevents the dashboard/API/MCP/warehouse scaffold from diluting the core parser, model, provenance, publication and validation coverage signal.

## Security validation

Bandit is now part of the installed quality gate. XML parsing uses `defusedxml` so that MBS-like XML fixtures and future local XML snapshots do not depend on unsafe stdlib XML parsing.

`pip-audit` remains in the development extra. It should be run in CI or a network-enabled local environment:

```bash
pixi run pip-audit
```

## Dashboard validation

The Astro/Cosmograph dashboard is now locally validated with a committed lockfile:

```bash
cd apps/dashboard
npm ci
npm audit --omit=dev --audit-level=moderate
npm run build
```

The build performs `astro check` and renders the graph, source, analysis, crosswalk, ontology and readiness routes from dashboard-safe CSV artefacts.

## Validation run record

The current local runs are summarised in `data/derived/v6_validation_run.json` and `data/derived/v7_validation_run.json`. They record passed checks as well as blocked checks such as network-dependent `pip-audit`.
