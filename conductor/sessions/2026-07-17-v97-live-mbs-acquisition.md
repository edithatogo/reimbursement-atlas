# Session v97: live MBS acquisition and derived bundle promotion

## Scope

Run the hardened source acquisition workflow, promote the current MBS TXT pair
into a derived-only bundle, and preserve the distinction between local
validation and publication approval.

## Evidence

- `20260701_MBSONLINE_IMAP.TXT` downloaded successfully to ignored local raw
  storage; 5,827,871 bytes.
- `20260701_MBSONLINE_DESC.TXT` downloaded successfully to ignored local raw
  storage; 8,580,935 bytes.
- Both source contracts passed.
- The derived bundle contains 14,856 `ScheduleItemRecord` rows.
- Item-map checksum:
  `f3c1caae2bce9610a05dff435e27ec40c91e0a7d6b3adb2b8ca89929b62a5b36`.
- Descriptor checksum:
  `1fe830ae80bfcd55f5815029331b0a4e02f5c70232408ce1e8861e3606f3498b`.
- Raw files were not copied into the derived bundle and local paths were
  redacted from snapshots.
- The bundle quality report records two descriptor-only rows and no blocking
  parse or contract failures.

## Boundaries

- The derived bundle remains `public_reuse_review` and records
  `review_required_before_publication: true`.
- The user's MBS licence confirmation is retained as context, but no unnamed or
  unattributed human publication approval is fabricated in the licence queue.
- PBS acquisition remains blocked by the absent
  `PBS_API_SUBSCRIPTION_KEY`.
- CMS CLFS, ASP and PFS payloads remain skipped until their source-specific
  licence/manual-review gates are resolved.

## Regenerated outputs

- Source download attempts, validation and contract reports.
- Reviewed-source bundle snapshots and validation report.
- Publication manifest, licence-review queue and research package.
- Seed lake, dashboard assets, release readiness and final handoff.
