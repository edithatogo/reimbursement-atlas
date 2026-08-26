# Source acquisition status

- Ingestion implementation: `complete`
- Coverage/evidence promotion: `partial`
- Status: `incomplete`
- Incomplete targets: `2`
- Operational blockers: `4`
- Licence-review targets: `7`
- This report performs no network I/O and no source-cache mutation.

## Actions

- `final_historical_source_expansion` (partial): Review historical MBS/PBS source expansion and licence scope
  Action: Review downloaded-source evidence and resolve remaining licence-gated or unacquired targets before promotion.
  Evidence: `data/derived/historical_sources/summary.json`
- `final_source_downloads` (partial): Run hardened curl/wget source download plan
  Action: Provide `PBS_API_SUBSCRIPTION_KEY` through the approved secret store, then rerun acquisition.
  Evidence: `data/derived/source_downloads/download_attempts.jsonl`
