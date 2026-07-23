# Mapping workbench

The mapping workbench adds a transparent pre-embedding baseline for cross-jurisdictional reimbursement
item mapping. It is intended for candidate triage, not automated equivalence.

Blinded validation uses the bounded family relations in
[`MAPPING_STUDY_CODEBOOK.md`](MAPPING_STUDY_CODEBOOK.md). Candidate scores and hypotheses are
hidden from reviewers, and each immutable study cycle retains its own checksum-bound packet,
review ledger, adjudication and holdout artifacts.

Current generated artefacts:

- `data/derived/vertical_slice/mapping_evidence_matrix.jsonl`
- `data/derived/vertical_slice/mapping_evidence_matrix.csv`
- `data/derived/vertical_slice/gold_standard_mappings.jsonl`
- `data/derived/vertical_slice/gold_standard_mappings.csv`
- `data/derived/vertical_slice/negative_controls.jsonl`
- `data/derived/vertical_slice/negative_controls.csv`
- `data/derived/vertical_slice/mapping_calibration_cases.jsonl`
- `data/derived/vertical_slice/mapping_calibration_cases.csv`
- `data/derived/vertical_slice/mapping_calibration_summary.jsonl`
- `data/derived/vertical_slice/mapping_calibration_summary.csv`
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

The calibration exports split the workbench into three reviewer surfaces:

- gold-standard fixtures that should be matched;
- negative controls that should stay unmatched;
- a summary row with recall, precision, specificity and a recommended review threshold.

Run the workbench artefacts:

```bash
pixi run vertical-slice
pixi run vector-seed
# optional local vector database; output is ignored by git
PYTHONPATH=src reimbursement-atlas vector-seed --build-lance
```

Policy use remains limited to identifying which item pairs deserve expert review. Do not use these
machine rows as billing, clinical or legal equivalence statements.

## Human adjudication contract

The optional `data/mapping_review/decisions.jsonl` file records human decisions
against the exact candidate identity and confidence. Its shape is defined by
[`data/mapping_review/decision.schema.json`](../data/mapping_review/decision.schema.json).
The schema requires a reviewer role, relationship decision, scope and unit
equivalence checks, evidence and rationale. It is approval-neutral: missing
decisions keep the mapping gate at `review_required`, and a recorded decision
does not override licence, clinical, research or release gates.
