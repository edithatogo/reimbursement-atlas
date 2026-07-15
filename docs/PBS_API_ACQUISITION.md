# PBS API acquisition

The PBS documentation confirms that the API is the current distribution mechanism for the
Schedule, is updated monthly, exposes JSON and CSV responses, and uses a shared public rate
limit. The documentation page is not a data extract.

## Current probe

On 2026-07-16 the candidate public route returned `401` with a missing-subscription-key error:

```text
https://data-api.health.gov.au/pbs/api/v3/schedules?format=json
```

The route and version must be confirmed from the current official PBS API Catalogue/Swagger
request definition before acquisition. The subscription key is an external credential and must
never be committed, printed, embedded in generated download plans, or written to provenance.

## Safe acquisition sequence

1. Obtain or provision the PBS API subscription key through the official API portal.
2. Resolve the current public Swagger request URL and record the endpoint/version as redacted
   provenance only.
3. Fetch the `schedules` endpoint first and select a published monthly `schedule_code`; do not
   assume the largest code is the latest schedule.
4. Fetch only the reviewed endpoint set, respecting the shared public rate limit of one request
   per 20 seconds.
5. Store raw responses only under ignored `data/raw_live/au_pbs/`.
6. Run source validation, source contracts and `parse_pbs_csv` against a reviewed CSV/JSON
   extract, then commit derived rows and redacted checksums only.

The current implementation remains fail-closed at the monthly-extract step. GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25)
tracks the required reviewed extract and licence decision.
