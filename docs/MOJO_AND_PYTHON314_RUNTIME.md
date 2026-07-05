# Mojo-first runtime and Python 3.14 posture

The project uses a stable-core/frontier-edge design.

- **Mojo** is the performance-kernel layer for fixed-width tokenisation, fuzzy prefiltering, vector pre-processing and future high-throughput graph construction.
- **Python 3.14** is the target orchestration/runtime branch for CLI, API, MCP, data contracts and packaging once the execution environment can install it.
- **Python 3.13** remains a temporary sandbox fallback because the current runtime could not download Python 3.14 from the uv standalone Python source.

The repo records this explicitly in `data/seed/runtime_targets.*`. Release CI should run Python 3.14 and should not treat the sandbox fallback as a public-release target.
