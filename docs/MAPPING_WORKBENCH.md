# Mapping workbench

The mapping workbench adds a transparent pre-embedding baseline for cross-jurisdictional reimbursement
item mapping. It is intended for candidate triage, not automated equivalence.

Current generated artefacts:

- `data/derived/vertical_slice/mapping_evidence_matrix.jsonl`
- `data/derived/vertical_slice/mapping_evidence_matrix.csv`
- `data/derived/vector_seed/schedule_item_vectors.jsonl`
- `data/derived/vector_seed/schedule_item_vectors.csv`
- `data/derived/vector_seed/schedule_item_vectors.arrow`

The evidence matrix combines:

- token Jaccard overlap;
- deterministic hash-vector cosine similarity;
- optional price-ratio signal;
- same-domain and same-currency flags;
- a review-priority score.

The hash-vector approach is deliberately simple and deterministic. It gives us a reproducible baseline
before introducing external embedding models, LanceDB approximate-nearest-neighbour search, ontology
crosswalks, or clinician-reviewed gold standards.

Run the workbench artefacts:

```bash
pixi run vertical-slice
pixi run vector-seed
# optional local vector database; output is ignored by git
PYTHONPATH=src reimbursement-atlas vector-seed --build-lance
```

Policy use remains limited to identifying which item pairs deserve expert review. Do not use these
machine rows as billing, clinical or legal equivalence statements.
