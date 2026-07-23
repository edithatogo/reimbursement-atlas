# Mapping study codebook

The mapping study evaluates bounded cross-source relationships, not universal billing-code
equivalence. Every case states one target relation before review:

| Family | Positive decision |
|---|---|
| Procedures and pathology | The records describe a clinically comparable service or test class suitable for grouped comparative analysis. They need not share billing rules, units or prices. |
| Medicines | The records support the same active ingredient or therapeutic moiety. Form, strength, route, reimbursement status and price may differ and must not be inferred. |
| Genomics and coverage | The service or coverage record and terminology record concern the same gene, phenotype, analyte or test-family linkage. This does not establish identical eligibility or coverage. |
| Devices and other | The records concern the same device class or intended use. Manufacturer, model, regulatory status and reimbursement are not inferred. |

Reviewers use `positive` only when the displayed evidence supports the stated relation. They use
`negative` when it contradicts or fails to support it, `uncertain` when additional permitted
evidence could resolve the case, and `exclude` for malformed, out-of-scope or rights-inadequate
evidence. Machine hypotheses, candidate scores and development/holdout assignment remain hidden.

The first two cycles predated this explicit estimand and remain immutable diagnostic evidence.
They must not be pooled with later codebook-bound reviews. A codebook-bound cycle uses v2
candidate, blinded-case and review schemas and retains its own frame checksum.
