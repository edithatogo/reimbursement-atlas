# Mojo extension layer

Mojo is reserved for later performance-critical kernels. Candidate modules:

- `parser_tokenizer.mojo`: high-throughput fixed-width/PDF-derived table tokenisation.
- `fuzzy_join.mojo`: string and embedding prefiltering for mapping candidates.
- `graph_edges.mojo`: fast construction of large source-item-concept graphs.

The first implementation should remain in typed Python until bottlenecks are measured with Scalene.
