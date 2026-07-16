# v78 fuzzy prefilter benchmark

## Scope

Advance `func_mojo_fuzzy_prefilter` from an unmeasured prototype to a reproducible,
review-gated benchmark under `track_runtime_mojo_python314`.

## Implemented

- Added `scripts/make_fuzzy_prefilter_benchmark.py` and the `pixi run fuzzy-benchmark` task.
- Benchmarked the Python reference over the reviewed synthetic gold-standard and negative-control
  fixtures at threshold `0.2`.
- Added CI and deterministic regeneration coverage.
- Added the benchmark to the publication manifest and runtime documentation.
- Regenerated evidence remains explicitly synthetic and publication-safe.

## Result

- Gold-standard pairs: 2; matched: 2; recall: `1.0`.
- Negative controls: 2; triggered: 0; specificity: `1.0`.
- Precision: `1.0`.

## Boundary

The roadmap function remains `prototype` and the report remains `review_required`. Real-source
gold-standard expansion and accountable human mapping adjudication are required before promoting
the kernel or claiming evidence-ready recall.
