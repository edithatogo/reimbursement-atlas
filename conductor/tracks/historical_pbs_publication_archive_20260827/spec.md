# Specification

## Objective

Discover and locally preserve the official PBS Schedule publication archive as ignored raw
evidence, then commit only deterministic target inventories, checksums, acquisition receipts and
reproducibility metadata.

## Acceptance Criteria

1. Discovery covers the official 1951-2002 archive and annual publication pages from 2003 onward.
2. The downloader preserves required URL query parameters, allowlists official hosts, bounds
   transfers and rejects HTML or other invalid content masquerading as PDF or ZIP payloads.
3. Successful files are stored only under ignored `data/raw_live/` paths; tracked outputs contain
   no raw publication payloads or local absolute paths.
4. Receipts record every target as downloaded, cached, upstream unavailable, invalid content or a
   retryable download failure without silently dropping failures.
5. Documentation states that publication PDFs are citable snapshots, not structured PBS API
   history or field-level reimbursement-data parity.
6. Medallion, backfill/replay, publication and dashboard projections include only the permitted
   inventory and receipt metadata.
7. Focused tests, public-data policy, deterministic generation and the protected hosted workflow
   pass before archival.
