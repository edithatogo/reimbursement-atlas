# Implementation plan

- [x] ING-01: Run the hardened 11-target acquisition plan and record redacted
  receipts. (LIVE-001)
- [x] ING-02: Validate downloaded source content and source contracts. (LIVE-001)
- [x] ING-03: Parse the real July 2026 MBS TXT pair into a derived-only bundle
  with checksums and redacted source snapshots. (LIVE-001)
- [x] ING-04: Run focused parser, source and public-data policy tests. (LIVE-001)
- [x] ING-05: Complete source-specific MBS reuse/licence and accountable content
  review before promoting the bundle beyond `public_reuse_review`. (LIVE-001)
- [x] ING-06: Validate CMS CLFS, ASP and PFS against permitted reviewed payloads
  without redistributing CPT/HCPCS-restricted descriptors. (LIVE-001)
- [x] ING-07: Refresh and validate the PBS API CSV parser with a credentialed,
  reviewed monthly extract through hosted source-health run 32951770117. (LIVE-001)

## Review fixes

- [x] REV-01: Add the missing track-local specification, plan, metadata and
  evidence ledger required by the Conductor review contract.
- [x] REV-02: Reconcile completed MBS, PBS, CLFS, ASP and PFS parser/source
  reviews against current bundle, validation and licence evidence. (Issue #749)
- [x] REV-03: Reconcile registry, metadata, seed projections and archive paths
  after all bounded track gates passed. (Issue #759)
