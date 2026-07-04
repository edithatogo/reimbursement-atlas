# Local quality-gate orchestration

The repository now has a single local quality-gate orchestrator that mirrors the main CI/CD checks and writes structured evidence for Conductor handoffs, GitHub Actions artefacts and release review.

```bash
uv run --all-extras python scripts/run_local_quality_gates.py --profile ci
```

Profiles:

| Profile | Purpose | Notes |
|---|---|---|
| `quick` | Fast developer sanity check | Lint, format, compile, seed sync and public-data policy. |
| `ci` | Pull-request parity | Python quality, tests, coverage, Bandit, build, dashboard install/audit/build, repo automation and SBOM generation. |
| `release` | Release review | CI profile plus advisory network-backed gates such as `pip-audit` and `zizmor`. |
| `nightly` | Long-running checks | Mutation testing and other trend gates that should not block ordinary PRs. |

Generated evidence is written to:

```text
data/derived/local_quality_gates/
```

The files include executable gate specifications, run records and a summary. A run is considered release-ready only when every blocking gate passes. Advisory gates may record `blocked_network`, `missing_tool` or `wrong_tool` without masking the result as a pass.

The GitHub workflow `.github/workflows/uv-quality.yml` runs the same orchestrator with the `ci` profile. This gives the project a uv-native CI path alongside Pixi so repository health is not entirely coupled to a single environment manager.
