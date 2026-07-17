# Source acquisition status

- Status: `incomplete`
- Incomplete targets: `1`
- Operational blockers: `1`
- Licence-review targets: `6`
- This report performs no network I/O and no source-cache mutation.

## Actions

- `final_source_downloads` (partial): Run hardened curl/wget source download plan
  Action: Provide `PBS_API_SUBSCRIPTION_KEY` through the approved secret store, then rerun acquisition.
  Evidence: `data/derived/source_downloads/download_attempts.jsonl`
