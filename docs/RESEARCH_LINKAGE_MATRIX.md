# Research linkage matrix

Research questions now resolve to explicit source, dataset-candidate, mapping-resource and output rows. This closes the loop between Conductor tracks, OSF protocols, GitHub issues and Hugging Face/dashboard outputs.

Run:

```bash
PYTHONPATH=src reimbursement-atlas roadmap-linkages
# or
PYTHONPATH=src python scripts/make_roadmap_linkages.py
```

Generated artefacts:

```text
data/derived/roadmap_linkages/research_dataset_linkages.jsonl
data/derived/roadmap_linkages/research_dataset_linkages.csv
```

The linkage matrix is used to identify missing dataset/source candidates before a research protocol is treated as implementation-ready. It also gives the GitHub Project a clear way to link research questions to source onboarding, mapping workbench tasks and output publication tasks.
