# Source acquisition status

- Status: `incomplete`
- Incomplete targets: `2`
- Operational blockers: `1`
- Licence-review targets: `7`
- This report performs no network I/O and no source-cache mutation.

## Actions

- `final_historical_source_expansion` (partial): Review historical MBS/PBS source expansion and licence scope
  Action: Review downloaded-source evidence and resolve remaining licence-gated or unacquired targets before promotion.
  Evidence: `data/derived/historical_sources/summary.json`
- `final_source_downloads` (review_required): Run hardened curl/wget source download plan
  Action: Complete the human source/licence review for the gated rows; no additional automated acquisition is required.
  Evidence: `data/derived/source_downloads/download_attempts.jsonl`
