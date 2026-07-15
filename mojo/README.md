# Mojo extension layer

Mojo is now an explicit performance-kernel track, not a vague future placeholder.

Current kernels:

- `fixed_width_tokenizer.mojo`: smoke-tested fixed-width byte tokenizer and pipe-count kernel. Its assertions exercise the same two-column behavior as the Python reference parser.
- `fuzzy_join.mojo`: token-Jaccard candidate prefilter prototype; its scores are triage signals, not mapping decisions.

Candidate kernels:

- fixed-width and TXT parsing tokenisers for MBS/CMS-style files;
- fuzzy string prefilters for mapping candidates;
- vector pre-processing and graph edge construction.

Reference implementations remain in typed Python first. A Mojo kernel requires:

1. a Python parity test or fixture;
2. a benchmark/scalene profile showing a bottleneck;
3. a CI smoke test;
4. documentation of any portability caveats.

Run:

```bash
scripts/run_mojo_smoke.sh
```

The parity report is generated with `pixi run mojo-parity` and stored at
`data/derived/mojo/mojo_parity_report.json`. It records the Python reference contract,
the bounded benchmark workload and whether the official Mojo smoke runtime was available;
missing Mojo is reported as an environment blocker rather than treated as a Python failure.
