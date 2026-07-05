# Public artefact data dictionary

The data dictionary describes candidate public artefacts before they are published to GitHub releases, Hugging Face Datasets, OSF or Zenodo. It records path, format, row count, columns, publication scope and licence gate.

Generate it with:

```bash
PYTHONPATH=src reimbursement-atlas data-dictionary
# or
PYTHONPATH=src python scripts/make_data_dictionary.py
```

Outputs:

```text
data/derived/data_dictionary/data_dictionary.jsonl
data/derived/data_dictionary/data_dictionary.csv
data/derived/data_dictionary/summary.json
```

The data dictionary is derived from the publication-manifest candidate path list and excludes raw/local/cache paths. It should be regenerated after any new public artefact is added, after schema changes, and before Hugging Face or OSF publication.
