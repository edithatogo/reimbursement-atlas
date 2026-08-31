# Historical source boundaries

Bounded revalidation on 2026-08-30 for issue #255. These are observations, not
source acquisition, licence clearance or proof that unpublished files never existed.

## MBS July 2026 TXT endpoints

The two historical URL failures refer to `20260701_MBSONLINE_DESC.TXT` and
`20260701_MBSONLINE_IMAP.TXT`. The corresponding official URLs in the live-source
registry use a different Domino view identifier from the historical inventory.
A bounded retry against those independently recorded alternatives also returned
HTTP 404 for both files. These are locator failures, not missing acquisition
evidence: both exact TXT identities already have validated checksum-bound source
snapshots in the reviewed TXT-pair bundle. The generated
`data/derived/historical_sources/mbs_identity_reconciliation.json` reconciles
source identity, version, byte size and checksum without changing HTTP receipts.
There are 341 direct historical download receipts and two reviewed snapshot
aliases: 343 target identities with acquisition evidence. Current raw-cache
availability is not asserted, and no new bytes or redistribution rights arise.

## December 1987 RPBS

The repository's bounded downloader returned HTTP 404 for the official
[base PDF URL](https://www.pbs.gov.au/publication/schedule/1951-2002/1987-12-01-RPBS-Schedule.PDF)
and HTTP 403 for the same URL with `?variant=3`. Neither response produced a
signature-validated payload. The indexed mobile-host link resolves to the PBS
homepage rather than the PDF. Search results containing the document's title or
text are not a recovered immutable PDF and must not count toward acquisition.

The existing CDX client returned zero matching captures for bounded queries of
the exact PDF path on both `www.pbs.gov.au` and `m.pbs.gov.au`, with its HTTP-200
and PDF-MIME filters. This does not establish absence from all web archives or
from differently named URLs. The known corpus remains 1,048 of 1,049 PDFs.

## December 2006 to March 2007 XML

The Department's [legacy XML documentation](https://data.pbs.gov.au/document/87239.html)
states that the G2B XML publication period began in December 2006. That is earlier
than the first acquired package in this repository, April 2007. The live 2006
archive page yielded no structured-package links; the 2007 page yielded 18, with
the earliest dated April 2007. Catalogue-link absence is not proof that earlier
machine-readable releases did not exist.

The documentation's [legacy schema archive link](https://data.pbs.gov.au/ps/data_source/website/website/downloads/schema-archive.html)
currently returns HTTP 404. The [historical schema presentation](https://data.pbs.gov.au/download/88817)
lists version 1.1.1 in December 2006, whereas the later legacy documentation
describes the wider G2B period in terms of schema 1.8. Do not assign schema 1.8
to every early release or infer field compatibility from either summary.

The precise request is therefore for the December 2006 and January-March 2007
release payloads, their release-specific schema/DTD/XSL files, amendments and
version identifiers. Any recovered release must have signature/archive-member
validation, checksums, provenance, rights review and a version-specific parser
contract before it is treated as a structured historical dataset.

## Remaining source boundary

Raw PBS redistribution is allowed on the owner's 2026-08-31 attestation, recorded
in [the permission documentation](PBS_RAW_REDISTRIBUTION_PERMISSION.md).
No additional owner permission receipt or per-file approval is required. This is
not represented as a publisher document independently verified by the project.

Publisher byte availability and release-specific schema recovery remain external
gaps. The source recovery request is prepared, not sent. Permission does not prove
acquisition or publication: keep raw files outside Git and verify any external
archive transfer separately.
