# Research claim decisions

`decisions.jsonl` is optional and owner-authored. Each row binds one research
question to a derived claim package by SHA-256. The evidence-readiness generator
accepts a row only when:

- the package is beneath `data/derived/research_claims/`;
- the recorded checksum matches the current file;
- `reviewed_derived_inputs` and `analysis_validated` are both `true`;
- `status` is `approved_within_scope`; and
- a bounded accountable `review_record` is present.

Protocol completeness, linkage scores, fixture demonstrators, mapping validation,
or registration state cannot substitute for this decision. Papers and preprints
remain outside this contract.
