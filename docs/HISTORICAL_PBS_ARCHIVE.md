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
- `scripts/discover_historical_pbs_structured_archive.py` separately inventories official XML,
  CSV, ASCII/text and structured-extract packages; compressed PDF publication bundles are not
  labelled as machine-readable data.
- `scripts/download_historical_sources.py` stores acquired PDFs only under ignored
  `data/raw_live/historical_sources/` and writes tracked checksum-bound receipts.
- `scripts/make_pbs_archive_verification.py` compares local payload SHA-1 digests with Internet
  Archive CDX observations. A URL capture, search-index result or catalogue reference is not called
  byte verification unless the digest matches.
- `scripts/download_pbs_archive_variants.py` preserves differing Internet Archive replay bytes in
  ignored storage and verifies each replay against its CDX digest.
- `scripts/make_pbs_public_provenance.py` publishes only source URLs, checksums, archive
  observations, rights states and transformation metadata.
- A monthly archival process may copy responses only into ignored `data/raw_live/au_pbs/`
  storage, using the runtime-only `PBS_API_SUBSCRIPTION_KEY` and the published rate limit.
- Raw responses, source-derived rows and historical promotion remain subject to source terms,
  accountable licence review and the reviewed-source gates.
- No historical PBS PDF or API payload is tracked by this repository.
- Target and acquisition summaries report failed or unavailable upstream files explicitly; they do
  not infer completeness from a catalogue row or a successful archive-page request.

The repository therefore maintains three complementary lanes: rolling structured API acquisition,
historical structured-package preservation from April 2007 onward, and publication-PDF
preservation from 1951 onward. Only permitted metadata, checksums and transformation/provenance
records can be promoted; any raw redistribution, structured historical reconstruction or derived
research use remains independently gated.

It also maintains a separate utilisation lane. The Services Australia PBS Item Report indexed by
data.gov.au and Magda contains aggregate services and benefits paid by PBS/RPBS item and
state/territory. Its eight CSV, XLSX and ZIP resources cover historical 1992-2014 files plus
2015 and 2016 YTD releases under Creative Commons Attribution 3.0 Australia. These observations
can complement schedule publications, but they are processed-claims utilisation evidence, not
schedule prices, prescribing dates, supply dates, net prices or complete medicine coverage.

## Current bounded acquisition

The 2026-08-29 acquisition inventory contains 1,049 official publication PDF targets covering
1951-03-01 through 2026-07-01. The local ignored cache contains 1,048 signature-validated payloads
(99.9047% of targets; 6,246,978,558 bytes) with SHA-256 receipts. The December 1987 RPBS URL is the
only missing payload: it returns HTTP 403 with the required query and HTTP 404 without it.

The separate machine-readable inventory contains 655 official packages covering 2007-04-01
through 2026-07-01: 467 XML ZIPs, 103 structured-extract ZIPs, 66 text/ASCII ZIPs, 16 CSV ZIPs and
3 direct CSVs. All 655 are signature-validated in ignored storage (2,905,582,497 bytes). This is
broad structured-package preservation, but `structured_api_equivalence` remains false because
formats and field contracts change across periods.

The Internet Archive CDX observation contains 1,033 distinct captured PDF digests. Matching source
identity across HTTP and HTTPS transport variants, 690 local targets exactly match an archived
SHA-1 digest. Five current official files differ from an older archived capture; all five archived
variants were retrieved into ignored storage and match
their CDX digests. The December 1987 RPBS URL has no Internet Archive capture. Search indexing
exposes text from that publication and the official archive lists its identity, but neither
observation verifies the missing source bytes.

A bounded follow-up on 2026-09-01 inspected the NLA catalogue and request records. The serial is
available for use in the Main Reading Room and its holdings range includes December 1987, but the
record exposes no digitised copy. A targeted Internet Archive item search returned zero matches.
This changes the status from an uninspected catalogue lead to an inspected physical-access lead;
the target issue itself remains uninspected and unrecovered.

The same follow-up verified checksum-bound January and February 2007 archive indexes. They expose
December 2006, January 2007 and February 2007 FlashPaper publication views, not XML distributions.
Three bounded CDX prefix searches found no captured structured payloads under the tested historical
publication paths. This narrows the search boundary but does not prove that the releases never
existed. December 2006 through March 2007 monthly structured releases and release-specific
schema/DTD/XSL assignments therefore remain unrecovered. The deterministic receipt is
`data/derived/historical_sources/pbs_gap_research_v1/summary.json`.

This is broad publication and structured-package coverage, not a complete or schema-homogeneous
historical PBS dataset.

## Raw publication rights

The [PBS copyright terms](https://www.pbs.gov.au/info/general/copyright) reserve uses beyond
limited personal/reference reproduction. Download availability and local preservation do not grant
permission to republish the raw PDFs or structured packages under Apache-2.0 or another project
licence. Consequently, GitHub, Hugging Face and archive products contain the public provenance
catalogue, not raw PBS payloads. Raw publication can proceed only after the Department provides an
applicable open licence or written redistribution permission covering the intended repositories.
