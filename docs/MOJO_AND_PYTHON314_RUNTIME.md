# Mojo-first runtime and Python 3.14 posture

The project uses a stable-core/frontier-edge design.

- **Mojo** is the performance-kernel layer for fixed-width tokenisation, fuzzy prefiltering, vector pre-processing and future high-throughput graph construction.
- **Python 3.14** is the active orchestration/runtime branch for CLI, API, MCP, data contracts and packaging. The current environment validates Python 3.14.6 through official Pixi and Python 3.14.5 through uv.
- **Python 3.13** remains a compatibility fallback only for environments that cannot install or run Python 3.14.
- GitHub Actions and the current local Pixi environment exercise the Python 3.14 runtime path directly.

The repo records this explicitly in `data/seed/runtime_targets.*`. Release CI should run Python 3.14 and should not treat the sandbox fallback as a public-release target.

The first executable kernel is `mojo/fixed_width_tokenizer.mojo`. It uses
byte-range slices for fixed-width source records and asserts parity with the
two-column Python reference fixture before emitting its smoke result. The
kernel remains intentionally small until profiling demonstrates a production
bottleneck; it does not replace the auditable Python parser by default.

`mojo/fuzzy_join.mojo` adds a bounded whitespace-token Jaccard prefilter
prototype. Its output is a candidate score only and remains subject to the
Python evidence pipeline, negative controls, and human adjudication.

`data/derived/mojo/mojo_parity_report.json` records the Python reference contract,
the bounded parity workload, deterministic workload fingerprints and the official Mojo smoke result. A missing Mojo
runtime is recorded as an environment blocker; it cannot promote or invalidate
the evidence-readiness status of the data product.

The fixed-width tokenizer is implemented but review-gated. Its benchmark contract records
input/output operation counts and canonical SHA-256 fingerprints, not machine-specific timing;
this makes regeneration comparable across runners without presenting a synthetic performance
claim. The fuzzy prefilter remains a prototype until gold-standard recall has been adjudicated.
