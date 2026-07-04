# ADR 0020: Deterministic vector mapping before embeddings

## Status

Accepted.

## Context

Cross-jurisdictional reimbursement mapping is policy-sensitive. Embeddings and vector databases are useful,
but they can obscure why two items were paired and can create false confidence before a reviewed gold
standard exists.

## Decision

Use transparent deterministic mapping evidence first:

- token Jaccard overlap;
- hash-vector cosine similarity;
- price-ratio signal;
- same-domain and same-currency flags;
- explicit review priority.

Export these rows to JSONL/CSV and a small Arrow vector seed. LanceDB remains an optional local index for
experiments, not a public source of truth.

## Consequences

The atlas gets a reproducible mapping baseline that can be benchmarked against future LOINC/RxNorm/ATC/UMLS
or embedding-backed approaches. All outputs remain review queues, not definitive mappings.
