# Autonomous continuation queue

Operational follow-up: issue #791, Conductor
`standing_low_risk_authorization_20260830`; implementation merged in PR #790.

## Execution contract

Continue the following queue in one execution without routine confirmation. Each
completed step advances to the next; stale machine evidence is not an owner
approval request. Preserve the original human record and apply standing scope.
Do not create duplicate publications or evaluate an accepted holdout again.

1. Verify the latest successful `main` Dashboard browser matrix run and its exact
   tested commit. Download its named review artifact, retain screenshots locally,
   and ingest only the generated automated/owner packet JSON files. Validate
   `dashboard_review_approved` and review schemas before claiming renewal.
2. Regenerate release readiness, final handoff, source drift, lineage, replay,
   research packaging, seed lake and dashboard projections to a deterministic
   fixed point. Run native local quality and hosted protected-branch checks.
3. Review and merge the scoped PR, verify its merged tree, synchronize `main`,
   and remove only the verified merged branch. Do not request approval for new
   packet hashes within the delegated route/browser/source scope.
4. Read-only verify existing Hugging Face and Zenodo metadata/file parity using
   the existing receipts and repository-native tools. Repair a local metadata
   defect through a PR; never recreate an existing draft or repeat publication
   merely because old handoff prose says to do so. New release publication must
   satisfy its own current gates and existing authorization scope.
5. Under #255, use bounded publisher/archive retries and source discovery for
   December 1987 PBS and December 2006-March 2007 XML/schema history. Verify signatures,
   checksums, source versions and provenance. Retain raw bytes only in ignored
   storage; report missing sources as gaps, not negative research evidence.
6. Recheck the existing #362 TypeScript/Astro compatibility canary. Upgrade only
   after typed checker support and repository gates pass. Unsupported versions
   stay monitored and do not block repository release.
7. Regenerate a final handoff bundle only after this delivery and any selected
   external-state updates settle. Preserve durable prior recovery archives;
   exclude raw restricted data and secrets from the handoff.

## Contingencies and stopping conditions

A bounded official-URL retry on 2026-08-30 still returned HTTP 403 for the
December 1987 RPBS PDF. No source bytes were acquired or published by that check.
The prepared publisher request is in `docs/PBS_RAW_REDISTRIBUTION_PERMISSION.md`.

Read-only run 33296198213 originally stopped at local inventory validation before
the remote API call. PRs #793/#794 fixed canonical attestation selection and DOI
content handling. Run 33301360240 subsequently verified the existing public
deposition `21759294` for `v0.1.1`: all 12 file checksums, metadata, DOI and
DataCite checks passed without mutation. Issues #791/#792 are closed. Do not
repeat draft creation or publication because an older failed receipt remains.

- Failed machine checks: fix and retry within a bounded diagnostic loop; record
  reproducible failures without weakening gates or asking for routine approval.
- Expired/missing hosted artifacts: rerun the browser workflow on the intended
  commit rather than pretending the old packet tests new content.
- Publisher 403/404 or missing archive bytes: preserve the verified corpus and
  exact unresolved target; prepare a publisher request rather than invent data.
- Raw PBS redistribution: apply the owner's 2026-08-31 permission attestation in
  `data/licence_review/pbs_raw_permission.json`; do not request another document
  or per-file approval. Preserve notices and provenance, and verify external
  publication separately. Other sources retain their own rights boundaries.
- Credentials: use configured secret channels without logging values. Stop only
  when remediation genuinely needs account-owner interaction.
- Papers/preprints, new rights/claims, destructive changes and external actions
  outside existing authorization remain excluded. Group genuinely necessary
  decisions, but do not batch routine refreshes into an approval packet.

This queue is a runbook, not a background scheduler. A continuous agent execution
can perform repository work and bounded retries; execution after the session ends
requires an explicitly configured automation. External availability cannot be
guaranteed by either mode.
