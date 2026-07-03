# Coverage policy

The project enforces a 90% minimum coverage threshold over the core Python library.

## Included by default

The coverage gate includes the code that currently carries the largest correctness and policy risk:

- Pydantic contracts and registry models;
- source-quality and readiness scoring;
- fixture and first-wave parsers;
- provenance and snapshot records;
- reviewed-source bundle generation;
- publication manifest generation;
- seed synchronisation and validation;
- source-acquisition and ingestion planning;
- policy signal and crosswalk helpers.

## Temporarily excluded

The following files are excluded from the coverage denominator until they mature beyond scaffold status:

| File | Reason |
|---|---|
| `api.py` | Optional read-only FastAPI shell. |
| `cli.py` | Typer wrapper around tested library functions. |
| `mcp_server.py` | Optional read-only MCP shell with lazy dependency import. |
| `parsers/base.py` | Abstract protocol/interface definitions. |
| `warehouse.py` | Optional DuckDB/Polars local warehouse path. |

These surfaces still have smoke or integration tests where feasible; they are just not allowed to distort the core coverage signal.

## Promotion rule

A file should leave the coverage omit list when it becomes a production surface or starts containing non-trivial business logic.
