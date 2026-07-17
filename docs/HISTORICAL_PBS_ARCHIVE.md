# Historical PBS Archive Boundary

The PBS public API is a monthly distribution mechanism, not an unlimited historical
archive. The official [PBS API documentation](https://data.pbs.gov.au/document/91327.html)
states that thirteen months of schedules, including the most recent schedule, are retained in
the public data mart. Schedule codes identify effective months and revisions.

## Repository policy

- The source registry records the PBS public cadence as `monthly`.
- The API's rolling window must not be represented as complete historical coverage.
- A monthly archival process may copy responses only into ignored `data/raw_live/au_pbs/`
  storage, using the runtime-only `PBS_API_SUBSCRIPTION_KEY` and the published rate limit.
- Raw responses, source-derived rows and historical promotion remain subject to source terms,
  accountable licence review and the reviewed-source gates.
- No historical PBS payloads are tracked by this repository.

The current repository therefore records the retention boundary and acquisition contract, while
the actual long-term archive remains an external or local operational responsibility until source
terms and an accountable review decision permit promotion.
