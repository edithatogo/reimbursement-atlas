# Bounded early PBS schema recovery

Observation date: 31 August 2026. This isolated evidence package is for parent
integration into the later source/archive track after #801. It does not update
canonical inventories, permission records, coverage projections or track status.

## Acquisition outcome

| Evidence class | Recovered |
| --- | ---: |
| Historical schema distributions | 2 |
| December 2006-March 2007 monthly releases | 0 |
| December 1987 RPBS PDFs | 0 |

The [official schema archive](https://data.pbs.gov.au/downloads/schema-archive.html)
works even though the longer legacy documentation URL under
`/ps/data_source/website/website/downloads/schema-archive.html` returns 404.

| Official package | Index source date | Acquired bytes | SHA-256 |
| --- | --- | ---: | --- |
| [v1.1.1](https://data.pbs.gov.au/download/schema-archive/v1/v1.1.1.zip) | 2006-11-29 | 5,289,495 | `728d2999fc2311317634013d9b30637d0d041391efd55914bada8e71a3ad5388` |
| [v1.2](https://data.pbs.gov.au/download/schema-archive/v1/v1.2.zip) | 2007-02-06 | 4,600,602 | `b1a8aaa788bc962e1be65605e204e311648f37bc3d7800cc73a5e7c2e3e00ae9` |

Both transfers completed with HTTP 200. Initial 30-second transfers were partial;
one explicit 90-second follow-up per package completed. Partial transfers are not
acquisition receipts. Dates above come from the official index, not inferred
monthly deployment. The v1.2 package includes member timestamps of 1 March 2007,
which differ from its index date.

## Verification and limits

- SHA-256 was calculated over each complete acquired ZIP; signatures were ZIP magic
  `504b0304`. Python `zipfile.ZipFile.testzip()` passed for every outer and nested
  archive member. Nested packages contain 45 and 44 non-directory files respectively.
- Python `xml.etree.ElementTree.fromstring()` parsed 19 and 22 XML-family members
  respectively, including nested files, with zero parse errors. Inspection read
  nested ZIPs in memory without fetching external resources. This verifies XML
  well-formedness, not RELAX NG/XSD compilation or release-specific validation.
- Basic RELAX NG metadata internally identifies versions 1.1.1 and 1.2. Packages
  include basic/full RELAX NG, compact schemas, XSD/support files, documentation,
  revision histories and illustrative XML. No standalone DTD or XSL was recovered.
- **Illustrative sample XML is not monthly-release evidence.** The documentation
  describes small hand-edited examples. December/January dates in those examples
  do not establish full release acquisition, publication, completeness or the
  schema used by any missing monthly release. No sample text is reproduced here.
- No missing-month amendment, monthly schema assignment, parser contract, API
  equivalence or independent archive checksum of either schema ZIP is verified.

## Internet Archive index verification

| Exact HTML replay | CDX SHA-1 base32, equal to replay digest |
| --- | --- |
| [January 2007 publication index](https://web.archive.org/web/20070117165023id_/http://www.pbs.gov.au:80/html/healthpro/publication/list) | `B64NEBSXS6XW23DK7T4LHVH2DA3GXSKE` |
| [February 2007 publication index](https://web.archive.org/web/20070221223532id_/http://www.pbs.gov.au:80/html/healthpro/publication/list) | `T22SJSY3YQREGOBZK4OY2TAQYSORH6WT` |
| [May 2023 schema archive index](https://web.archive.org/web/20230529194213id_/https://data.pbs.gov.au/downloads/schema-archive.html) | `KUM6VHDJG5KDXITU53USPMFL7QEMQQ3K` |

For each replay, SHA-1 of the acquired HTML bytes was base32 encoded and compared
with the corresponding CDX digest: three exact matches. Full query URLs, capture
timestamps, byte sizes, replay SHA-256 values and CDX response hashes are in
[summary.json](../data/derived/historical_sources/pbs_early_schema_recovery/summary.json).
This verifies only the HTML indexes, not their linked payloads. January/February
indexes provided publication-view links, not recovered missing XML releases.

Recovered schema documentation revealed the older
`https://www.pbs.gov.au/publications/2006/2006-12-01.xml` locator and sample
references using `-G2B.xml`. The five tested alternate December-March URLs, with
observed versus inferred naming distinguished in the summary, returned HTTP 404
website XML errors, not PBS schedules. XML content type alone is insufficient.
Bounded CDX empty results, timeouts and 503s do not prove archive-wide absence.

## December 1987 physical-copy lead

[NLA catalogue record 2271286](https://catalogue.nla.gov.au/catalog/2271286),
ISSN **0811-7705**, has a [read-only holdings panel](https://catalogue.nla.gov.au/catalog/2271286/request)
listing issues from 1983 no. 1 through 1985 no. 2 and August 1985 through
December 1987. Observed status: **Available**; location: **Main Reading Room**;
call number: **N 615.10994 REP**.

The catalogued range covers the target month. The actual issue was not inspected,
no digitised copy was acquired, and no library order or contact was made. This is
a physical serial holdings lead, not a PDF checksum or acquisition receipt.
The official [RPBS PDF URL](https://www.pbs.gov.au/publication/schedule/1951-2002/1987-12-01-RPBS-Schedule.PDF)
returned 404; its `?variant=3` form returned 403. The mobile-host link resolved to
the homepage, not a PDF. Trove/NLA web replay returned client-rendered shells;
Arquivo.pt timed out and Internet Archive item search failed TLS.

## Metadata-only handoff

[Acquisition receipts](../data/derived/historical_sources/pbs_early_schema_recovery/acquisition_receipts.jsonl)
contain only the two completed schema acquisitions. The summary separately records
index verification and catalogue observations. Raw ZIPs, samples, schemas, copied
documentation and absolute local paths are excluded. The existing owner permission
was accepted without requesting a new approval; this evidence makes no new rights
attestation. No publishers were contacted and nothing was uploaded or published.

The preceding investigation made 57 bounded scripted attempts, including one
local curl rejection before network access; additional web searches were bounded.
Limits were 10 seconds to connect, normally 30 seconds total, three redirects,
30 MB per response and no automatic retries. The two deliberate schema follow-ups
used 90-second limits. Unsuitable early wildcard queries were excluded from absence
reasoning. This metadata preparation uses retained evidence, not new publisher calls.

Run the offline metadata contract test from the repository root:

```sh
python -m pytest -q tests/unit/test_pbs_early_schema_evidence.py
```

The test validates metadata and claim boundaries only; it does not re-download,
re-hash raw payloads, compile schemas or inspect the NLA issue.
