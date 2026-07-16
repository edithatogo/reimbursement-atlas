# v132 real MBS acquisition and derived-only bundle

## Scope

Run the governed source-download plan, preserve redacted acquisition evidence, and convert the
first real July 2026 MBS TXT pair into a derived-only bundle without promoting licence or clinical
review status.

## Results

The hardened curl plan recorded nine attempts: two successful MBS downloads, six licence-gated
targets, and one PBS target blocked by the absent `PBS_API_SUBSCRIPTION_KEY`. The MBS pair was
parsed into 14,856 schedule rows. The bundle records item-map and descriptor checksums, has no raw
payload copies, and retains `public_reuse_review` plus the descriptor-only warning.

Derived evidence:

- `data/derived/source_downloads/download_attempts.jsonl`
- `data/derived/source_health/acquisition_status.json`
- `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/`

Issue #23 was updated with the evidence and remains open for clinical/licence review. Raw files
remain in ignored local storage and are not tracked.

## Decision

Treat the successful download and parser result as local acquisition evidence only. Do not close
the MBS review issue or upgrade evidence, publication, policy or research readiness until the
accountable human review is recorded.
