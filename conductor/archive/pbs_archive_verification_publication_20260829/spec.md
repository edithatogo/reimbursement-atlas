# Specification

## Objective

Verify official historical PBS publication files against independent web-archive observations,
discover downloadable structured PBS formats where available, and publish the maximum lawful
provenance product without representing archive metadata, indexed text or local possession as
source-byte verification or redistribution permission.

## Requirements

1. Query the Internet Archive CDX API for official PBS publication URLs and record capture time,
   original URL, digest, media type and length without importing archived payloads into Git.
2. Compare Internet Archive SHA-1 digests with locally preserved official payloads where both
   exist, and classify exact matches, mismatches, unverified captures and absent captures.
3. Record other independent verification observations, including official archive-page metadata,
   search-index discoverability and authoritative catalogue or legislation references, with an
   explicit evidence-strength classification.
4. Discover official CSV, XML, text and ZIP downloads separately from publication PDFs and retain
   format, period, provenance, checksum and rights state.
5. Publish checksum catalogues, provenance, source URLs, archive observations, transformation
   descriptions and permitted derived metadata.
6. Keep raw PDFs and structured payloads in ignored local storage unless a source-specific licence
   or written permission expressly permits public redistribution.

## Acceptance Criteria

1. Archive verification is deterministic from captured CDX responses and local receipt metadata.
2. A digest match requires identical bytes; indexed text or a catalogue reference is never called
   checksum verification.
3. The December 1987 RPBS record remains unresolved unless official or archived bytes are actually
   acquired and signature/checksum validated.
4. Structured-download discovery distinguishes XML/CSV/text archives from PDF publication history.
5. Public outputs contain no raw payload, restricted descriptor, credential or absolute local path.
6. Publication policy reflects the PBS copyright terms and fails closed on raw redistribution.
7. Tests, public-data policy, deterministic generation and hosted checks pass before archival.

## External Gates

- `pbs_raw_redistribution_permission`: written permission or an applicable open licence is required
  before raw PBS files can be republished.
- `pbs_1987_source_bytes`: publisher repair, authorised mirror or byte-preserving archive capture is
  required before the missing file can be marked acquired.

## Out of Scope

- Claiming complete structured historical PBS coverage from PDFs.
- Republishing raw PBS files under the repository's Apache-2.0 software licence.
- Causal, item-level coverage, price-equivalence, paper or preprint claims.
