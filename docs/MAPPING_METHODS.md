# Mapping methods

Cross-jurisdiction reimbursement comparison depends on mapping items that rarely align one-to-one.

## Mapping hierarchy

1. **Exact code match**: same code system and code version.
2. **Terminology-mediated match**: both sides map to the same external concept, such as LOINC, ATC or HPO.
3. **Descriptor-semantic match**: text similarity plus domain constraints.
4. **Basket-level match**: clinically meaningful basket rather than individual item equivalence.
5. **Policy-process match**: decision pathway or restriction architecture, not a price/item match.

## Evidence features

Candidate crosswalks should store:

- source and target code;
- relationship type;
- confidence;
- evidence methods;
- reviewer status;
- mapping notes;
- ontology dependencies;
- licence constraints.

## Similarity stack

Near-term:

- deterministic normalisation;
- token-based matching;
- ontology identifier joins where lawful;
- Polars/DuckDB candidate generation;
- clinician review queue.

Later:

- LanceDB semantic retrieval over descriptors and restrictions;
- embedding models evaluated on known mappings;
- Mojo kernels for high-throughput blocking/fuzzy matching;
- active-learning review interface.

## Clinical-review rule

No high-stakes policy inference should rely on an unreviewed mapping unless the output is explicitly labelled exploratory.
