# Session: v9 optional toolchains and mapping workbench

Date: 2026-07-04

## Summary

This pass added an optional-toolchain install/probe layer, manual acquisition-pack generation, a deterministic
mapping evidence matrix, vector seed exports and dashboard/readiness updates.

## Implemented

- Added `wrong_tool` external-gate classification.
- Added Mojo probe via `uv tool run --from mojo-compiler mojo --version`.
- Added official Pixi installer/on-PATH probes, including wrong-PyPI-package detection.
- Added manual acquisition pack generation from exact source-file records.
- Added `MappingEvidenceRecord` and mapping evidence matrix generation.
- Added deterministic hash-vector rows and optional Arrow/LanceDB vector seed CLI.
- Added dashboard tables for mapping evidence, manual acquisition steps and optional toolchain probes.
- Extended seed-lake manifest to include optional Parquet and DuckDB local materialisation when available.

## Validation

- Ruff passed.
- Ruff format check passed.
- basedpyright passed with 0 errors, 0 warnings, 0 notes.
- pytest/coverage passed: 91 tests, 91.78% core coverage.
- Generated vertical slice now includes 8 mapping evidence rows.
- Generated manual acquisition pack includes 7 exact source-file steps.
- External gates recorded: pip-audit blocked by DNS, npm audit passed, Pixi wrong/missing depending PATH, Mojo passed via uv tool.

## Handoff

Next pass should perform a reviewed local parse of the real MBS July 2026 TXT pair after manual download,
then compare the derived output against the synthetic parser contract without committing raw files.
