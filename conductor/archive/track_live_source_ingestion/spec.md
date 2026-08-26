# Evidence-grade live-source ingestion

## Scope

Acquire official public source payloads into ignored local storage, bind each
attempt to provenance and checksums, validate content and source contracts, and
publish only permitted derived records. Download success is not licence or
research approval.

## Acceptance criteria

- Acquisition uses HTTPS-only, retrying, redacted and reproducible receipts.
- Raw payloads remain outside tracked files and generated metadata contains no
  absolute local paths or credentials.
- Source-content and source-contract validation report pass, skip and failure
  states without converting skips into passes.
- Real parser outputs bind to source version, checksum, transformation metadata
  and publication licence state.
- Credential, source-rights and accountable-review gates remain fail-closed.
- The track is not complete or archivable while a required LIVE-001 review gate
  is blocked.
