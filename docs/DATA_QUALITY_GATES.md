# Data quality gates

The atlas now treats data quality as a generated release gate rather than an informal review step.

The v16 data-quality report checks:

- minimum row counts for core seed and derived tables;
- unique non-empty identifiers in registries;
- referential integrity across source files, source versions, Conductor tracks, roadmap functions, research questions and output plans;
- presence of generated artefacts required for release review;
- absence of raw-source payloads from the publication manifest;
- warning counts that require reviewer acknowledgement before publication.

Run:

```bash
PYTHONPATH=src reimbursement-atlas data-quality
# or
PYTHONPATH=src python scripts/make_data_quality_report.py
```

Generated artefacts:

```text
data/derived/data_quality/data_quality_checks.jsonl
data/derived/data_quality/data_quality_checks.csv
data/derived/data_quality/summary.json
```

A public release should have zero blocking failures. Advisory warnings can be accepted only when documented in the release notes or a project ADR.
