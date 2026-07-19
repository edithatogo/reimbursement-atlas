# PBS Review Decision

Use this form for issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25).

## Candidate

- Source: PBS API v3 public schedule, `schedule_code=4706`
- Effective date: `2026-07-01`
- Evidence: `data/derived/source_downloads/pbs_api_acquisition.jsonl`
- Summary: 10 schedules, 14,840 items, 17 fees; `schema_failures=0`
- Raw cache: ignored `data/raw_live/au_pbs/`; never commit raw payloads or headers

## Reviewer decision

- Reviewer: `repository-owner`
- Reviewed at: `2026-07-19`
- Decision: `approved` for the three checksum-bound PBS derived acquisition artefacts
- Source terms URL: [PBS API](https://data.pbs.gov.au/document/91327.html) and [PBS Downloads](https://www.pbs.gov.au/info/browse/download)
- Attribution text: Australian Government Department of Health and Aged Care, Pharmaceutical Benefits Scheme public API/download metadata; retrieved and derived by Reimbursement Atlas.
- Redistribution permission: Derived, field-limited artefacts only; raw source payload redistribution remains excluded.
- Allowed fields: identifiers, schedule metadata, drug/form/programme fields, restriction indicators, schedule/list-price fields, and `schedule_code`/effective-date joins.
- Excluded fields: raw payloads, credentials, request headers, local paths, confidential data, and net-price claims.
- Restrictions and caveats: Prices must remain labelled as schedule/list or payment values. This is not evidence, research, policy or publication approval for the wider project.
- Evidence/reference: User approval in the 2026-07-19 Codex session; `data/licence_review/decisions.jsonl`; `docs/SOURCE_FIELD_LICENCE_MATRIX.md`.

## Required confirmations

- [x] Item and fee rows are joined to effective date through `schedule_code` and `/schedules`.
- [x] Published prices are labelled as schedule/list or payment values, not net prices.
- [x] Credentials, headers, raw payloads, and local paths are excluded from publication.
- [x] Restriction text and drug-name handling are explicitly approved or excluded.
- [x] Decision is recorded in `data/licence_review/decisions.jsonl`.
