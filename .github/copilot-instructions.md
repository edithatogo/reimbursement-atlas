# Repository-specific AI coding instructions

- Do not commit raw live source files, local cache paths, restricted ontology dumps or confidential net prices.
- Prefer derived-only artefacts with explicit provenance, checksums and licence gates.
- Run `uv run --all-extras ruff check .`, `uv run --all-extras basedpyright`, and coverage before opening code changes.
- Regenerate repo automation and SBOM artefacts after changing `.github/**`, `pyproject.toml`, `uv.lock` or `apps/dashboard/package-lock.json`.
- Treat `conductor/context/CURRENT_FOCUS.md` and `conductor/DECISION_LOG.md` as the project handoff surface.
- For GitHub Actions changes, check `data/derived/repo_automation/workflow_policy.csv` and resolve any new `fail` records.
