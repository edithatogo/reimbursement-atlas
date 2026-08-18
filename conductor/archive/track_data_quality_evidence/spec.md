# Data quality, source validation and evidence readiness

## Scope

Make source-content validation, source contracts, record-count/schema checks,
data-quality reports, research-question linkage and evidence-readiness status
explicit and reproducible release gates.

## Acceptance criteria

- Source validation and source contracts emit deterministic, redacted reports
  without exposing raw payloads or local absolute paths.
- Data-quality checks cover required derived artefacts and distinguish warnings,
  failures, missing sources and licence/review blockers.
- Evidence-readiness rows link each research question to reviewed-derived source
  inputs, package checksums and bounded claim status.
- Dashboard and release projections consume the same generated gate state.
- Licence review, real-source sufficiency and accountable research review remain
  explicit blockers; passing computation does not imply evidence readiness.
