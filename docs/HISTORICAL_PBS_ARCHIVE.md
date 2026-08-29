# Historical PBS Publication Archive Boundary

The PBS public API is a monthly structured distribution mechanism, not an unlimited historical
archive. The official [PBS API documentation](https://data.pbs.gov.au/document/91327.html)
states that thirteen months of schedules, including the most recent schedule, are retained in
the public data mart. Schedule codes identify effective months and revisions.

The official [PBS Publications Archive](https://www.pbs.gov.au/info/publication/schedule/archive)
separately provides downloadable Schedule publication PDFs from 1951 onward. These publications
are useful as citable historical snapshots, but PDF preservation does not recreate historical API
responses and does not establish field-level structured-data parity.

## Repository policy

- The source registry records the PBS public cadence as `monthly`.
- The API's rolling window must not be represented as complete historical coverage.
- `scripts/discover_historical_pbs_archive.py` inventories official publication PDFs and preserves
  required download query parameters.
- `scripts/download_historical_sources.py` stores acquired PDFs only under ignored
  `data/raw_live/historical_sources/pbs_archive/` and writes tracked checksum-bound receipts.
- A monthly archival process may copy responses only into ignored `data/raw_live/au_pbs/`
  storage, using the runtime-only `PBS_API_SUBSCRIPTION_KEY` and the published rate limit.
- Raw responses, source-derived rows and historical promotion remain subject to source terms,
  accountable licence review and the reviewed-source gates.
- No historical PBS PDF or API payload is tracked by this repository.
- Target and acquisition summaries report failed or unavailable upstream files explicitly; they do
  not infer completeness from a catalogue row or a successful archive-page request.

The repository therefore maintains two complementary lanes: rolling structured API acquisition
and local preservation of historical publication PDFs. Only permitted metadata, checksums and
transformation/provenance records can be promoted; any structured historical reconstruction or
derived research use remains independently gated.

## Current bounded acquisition

The 2026-08-29 acquisition inventory contains 1,049 official publication PDF targets covering
1951-03-01 through 2026-07-01. The local ignored cache contains 938 signature-validated payloads
(89.4185% of targets; 4,658,177,952 bytes) with SHA-256 receipts. Of the remaining 111 targets,
110 exceeded the bounded transfer time and one official URL returned HTTP 403. These rows remain
explicitly `download_failed`; they are neither silently discarded nor counted as evidence.

This is broad publication-archive coverage, not a complete structured historical PBS dataset.
Future retries may improve the PDF count, while historical structured parity remains unavailable
unless an independently rights-cleared structured source is identified and validated.
