# v76 Mojo tokenizer benchmark contract

## Scope

Add deterministic benchmark evidence for the fixed-width Mojo tokenizer and close its roadmap
function without overstating machine-specific performance.

## Local evidence

- The Mojo fixed-width kernel passes the official smoke command.
- The typed Python reference passes the parity cases.
- The generated report records input bytes, output token counts and canonical SHA-256 workload
  fingerprints.

## Boundary

The tokenizer is implemented but review-gated. The benchmark is a reproducible workload contract,
not a timing claim. The fuzzy prefilter remains a prototype until gold-standard recall and human
mapping review are complete.
