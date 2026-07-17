# Conductor Session: v171 Authenticated Local PBS Acquisition

Date: 2026-07-17
Commit: working tree after `353b368`

## Scope

Use the official PBS API catalogue's published unregistered-user key only at runtime, run the
hardened acquisition layer, regenerate redacted source evidence, and verify that no key or raw
source payload enters tracked output.

## Evidence

- `/schedules`: 10 records, downloaded to ignored local raw storage.
- `/items`: 14,840 records across two existing ignored CSV pages.
- `/fees`: 17 records across the existing ignored CSV response.
- Redacted evidence: `data/derived/source_downloads/pbs_api_acquisition.*`, four rows,
  `review_status=acquired_unreviewed`, `raw_payloads_tracked=false`.
- Source validation: zero blocking failures; two executable records passed and seven licence-gated
  records were skipped.
- Source contracts: zero blocking failures; two executable records passed and seven were skipped.
- Source health: `review_required`, zero operational blockers, six licence-review targets.
- Public-data policy: passed; raw cache remains untracked and no absolute path or key is present in
  generated metadata.

## Boundary

This resolves the local `PBS_API_SUBSCRIPTION_KEY` acquisition blocker only. Human licence,
field-scope and research review remain required before the PBS-derived candidate can be published.
