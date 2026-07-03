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
PYTHONPATH=src ruff check .
PYTHONPATH=src ruff format --check .
PYTHONPATH=src basedpyright
PYTHONPATH=src pytest --cov=src/reimburse_atlas --cov-report=term-missing --cov-report=xml --cov-fail-under=90 -q
PYTHONPATH=src bandit -q -c pyproject.toml -r src scripts
PYTHONPATH=src python -m compileall -q src scripts tests
uv build
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
pip-audit --strict
```

## Dashboard validation

The Astro/Cosmograph dashboard remains scaffolded for Node validation:

```bash
cd apps/dashboard
npm install
npm run build
```

The Python runtime used for v6 did not complete Node dependency installation, so the dashboard build should remain a required follow-up check in GitHub Actions once a package lock is generated.

## Validation run record

The current local run is summarised in `data/derived/v6_validation_run.json`. It records passed checks as well as blocked checks such as network-dependent vulnerability audit or Node package-lock generation.
