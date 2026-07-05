# ADR 0028: Executable source download gates

Status: accepted

## Decision
Provide curl/wget/API acquisition commands and attempt logging, but enforce licence gates before auto-download.

## Consequences
- Public-file records can be downloaded to ignored local raw storage.
- Metadata-only, landing-page and restricted/licence-clickthrough records are skipped.
- Download failures are classified as blocked network, failed or skipped licence gate.
