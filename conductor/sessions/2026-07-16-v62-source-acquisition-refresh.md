# Session v62: source acquisition refresh

Date: 2026-07-16

## Scope

Reran the hardened source-download workflow and regenerated source validation, source
contracts, final handoff, source-health, data-quality, dashboard seed and release-readiness
outputs.

## Evidence

- Nine configured source records were attempted.
- The July 2026 MBS item-map and descriptor TXT pair downloaded to ignored
  `data/raw_live/au_mbs/` storage.
- Both MBS files passed source-content validation and MBS source-contract validation through
  the existing reviewed derived bundle.
- PBS API acquisition is blocked because `PBS_API_SUBSCRIPTION_KEY` is absent.
- Historical MBS and CMS CLFS/ASP/PFS records remain licence-gated or landing-page/manual
  review targets; no restricted payloads were auto-promoted.
- `git ls-files data/raw_live` remains empty.
- Data quality: 41/41 checks passed.
- Local quality: 27/27 gates passed.
- External quality: 7/7 gates passed.
- Release readiness: 36/36 gates passed; repository release is ready, but research
  publication, OSF registration, evidence release and policy claims remain blocked by
  human review, credentials and/or publication governance.

## Next actions

1. Supply PBS API credentials through the approved secret store and rerun acquisition.
2. Complete licence review before adding historical MBS or CMS-derived coverage outputs.
3. Complete human methods, mapping and research review before OSF/Hugging Face publication.
