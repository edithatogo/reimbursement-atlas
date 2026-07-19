# PBS Review Decision

Use this form for issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25).

## Candidate

- Source: PBS API v3 public schedule, `schedule_code=4706`
- Effective date: `2026-07-01`
- Evidence: `data/derived/source_downloads/pbs_api_acquisition.jsonl`
- Summary: 10 schedules, 14,840 items, 17 fees; `schema_failures=0`
- Raw cache: ignored `data/raw_live/au_pbs/`; never commit raw payloads or headers

## Reviewer decision

- Reviewer:
- Reviewed at:
- Decision: `approved` / `blocked`
- Source terms URL:
- Attribution text:
- Redistribution permission:
- Allowed fields:
- Excluded fields:
- Restrictions and caveats:
- Evidence/reference:

## Required confirmations

- [ ] Item and fee rows are joined to effective date through `schedule_code` and `/schedules`.
- [ ] Published prices are labelled as schedule/list or payment values, not net prices.
- [ ] Credentials, headers, raw payloads, and local paths are excluded from publication.
- [ ] Restriction text and drug-name handling are explicitly approved or excluded.
- [ ] Decision is recorded in `data/licence_review/decisions.jsonl`.
