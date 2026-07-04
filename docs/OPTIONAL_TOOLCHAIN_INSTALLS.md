# Optional toolchain install probes

The repo distinguishes the core validated toolchain from optional external toolchains.

Core quality gates use `uv`, Ruff, basedpyright, pytest/coverage, Bandit, Node/npm and Astro. Optional
gates now include:

- Mojo via `uv tool run --from mojo-compiler mojo --version`;
- official Pixi detection on PATH;
- official Pixi installer reachability;
- pip-audit strict advisory lookup;
- npm production audit.

Generate the optional install report:

```bash
PYTHONPATH=src python scripts/install_optional_toolchains.py
PYTHONPATH=src python scripts/run_external_quality_gates.py
```

Generated files:

- `data/derived/optional_toolchain_installs.json`
- `data/derived/optional_toolchain_installs.csv`
- `data/derived/external_quality_gates.json`
- `data/derived/external_quality_gates.csv`

## Pixi caution

`pixi` must mean the official Prefix.dev single-executable package manager. A same-named PyPI package
exists and is not the intended tool. The gate classifier now records that case as `wrong_tool` rather
than `passed` or `missing_tool`.

If the official installer is reachable, install Pixi using the official Prefix.dev instructions, not the
PyPI package named `pixi`.

## Mojo status

Mojo is treated as an optional accelerator layer. The repository should keep Python/Pydantic/Polars/Arrow
as the reference implementation until the source contracts and mapping semantics are stable.
