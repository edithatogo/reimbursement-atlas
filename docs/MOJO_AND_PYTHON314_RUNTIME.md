# Mojo-first runtime and Python 3.14 posture

The project uses a stable-core/frontier-edge design.

- **Mojo** is the performance-kernel layer for fixed-width tokenisation, fuzzy prefiltering, vector pre-processing and future high-throughput graph construction.
- **Python 3.14** is the target orchestration/runtime branch for CLI, API, MCP, data contracts and packaging once the execution environment can install it.
- **Python 3.13** remains a temporary sandbox fallback because the current runtime could not download Python 3.14 from the uv standalone Python source.
- GitHub Actions now exercises the Python 3.14 runtime path directly, while the sandbox fallback remains a local-only escape hatch.

The repo records this explicitly in `data/seed/runtime_targets.*`. Release CI should run Python 3.14 and should not treat the sandbox fallback as a public-release target.

The first executable kernel is `mojo/fixed_width_tokenizer.mojo`. It uses
byte-range slices for fixed-width source records and asserts parity with the
two-column Python reference fixture before emitting its smoke result. The
kernel remains intentionally small until profiling demonstrates a production
bottleneck; it does not replace the auditable Python parser by default.

`mojo/fuzzy_join.mojo` adds a bounded whitespace-token Jaccard prefilter
prototype. Its output is a candidate score only and remains subject to the
Python evidence pipeline, negative controls, and human adjudication.
