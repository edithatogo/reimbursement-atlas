# PBS API acquisition

The PBS documentation confirms that the API is the current distribution mechanism for the
Schedule, is updated monthly, exposes JSON and CSV responses, and uses a shared public rate
limit. The documentation page is not a data extract.

## Current probe

On 2026-07-16 the candidate public route returned `401` with a missing-subscription-key error:

```text
https://data-api.health.gov.au/pbs/api/v3/schedules?format=json
```

The official Department of Health API catalogue now provides the exact v3 details:

- API server: `https://data-api.health.gov.au/pbs/api/v3`
- OpenAPI export: `https://data-api-portal.health.gov.au/developer/apis/pbs-api-public-v3?export=true&api-version=2022-04-01-preview`
- Required header: `Subscription-Key`
- Relevant operations: `/schedules`, `/items`, and `/fees`
- Response formats: `application/json` and `text/csv`

The OpenAPI export is documentation metadata only. The subscription key is an external
credential and must never be committed, printed, embedded in generated download plans, or
written to provenance.

## Safe acquisition sequence

1. Obtain or provision the PBS API subscription key through the official API portal.
2. Use the catalogue's current v3 server and OpenAPI export above; do not infer endpoint paths
   from an older v2 integration.
3. Fetch the `schedules` endpoint first and select a published monthly `schedule_code`; do not
   assume the largest code is the latest schedule.
4. Fetch only the reviewed endpoint set, respecting the API's published rate limit and inspecting
   `X-Rate-Limit-Remaining` and `X-Rate-Limit-Limit` response headers.
5. Store raw responses only under ignored `data/raw_live/au_pbs/`.
6. Run source validation, source contracts and `parse_pbs_csv` against a reviewed CSV/JSON
   extract, then commit derived rows and redacted checksums only.

The source registry names `PBS_API_SUBSCRIPTION_KEY` as the runtime environment variable. The
acquisition helper returns a redacted `blocked_secret` attempt when it is absent; when present,
the value is passed only to the child HTTP process and is removed from command provenance.

The current implementation remains fail-closed at the monthly-extract step. GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25)
tracks the required reviewed extract and licence decision.
