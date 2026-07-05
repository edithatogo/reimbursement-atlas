# Source drift and schema-diff reports

Source drift is the controlled comparison of two tabular artefacts. In the current no-network state the default report checks JSONL/CSV mirror parity for key generated tables. Once real source snapshots are available, the same function can compare successive source-version outputs.

Generate the default report with:

```bash
PYTHONPATH=src reimbursement-atlas source-drift
# or
PYTHONPATH=src python scripts/make_source_drift_report.py
```

Compare two ad hoc files with:

```bash
PYTHONPATH=src reimbursement-atlas source-drift \
  --left-path data/derived/reviewed_sources/old.csv \
  --right-path data/derived/reviewed_sources/new.csv
```

Outputs:

```text
data/derived/source_drift/source_drift_report.jsonl
data/derived/source_drift/source_drift_report.csv
data/derived/source_drift/summary.json
```

Release interpretation:

- removed columns are breaking changes unless an ADR explains the change;
- row-count drift must be reviewed when comparing source versions;
- added columns require data-dictionary/dashboard updates;
- missing drift inputs block public release.
