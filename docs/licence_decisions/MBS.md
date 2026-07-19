# MBS Review Decision

Use this form for issue [#23](https://github.com/edithatogo/reimbursement-atlas/issues/23).

## Candidate

- Source: July 2026 MBS item-map and descriptor TXT pair
- Evidence: `docs/MBS_REVIEWED_PAIR_BUNDLE.md`
- Derived bundle: `data/derived/reviewed_source_bundles/`
- Raw cache: ignored `data/raw_live/au_mbs/`

## Reviewer decision

- Reviewer: `repository-owner`
- Reviewed at: `2026-07-19`
- Decision: `approved` for current-release XML and historical TXT-derived fields within the scope below
- Commonwealth/source terms URL:
- Attribution text:
- Redistribution permission:
- Allowed joined fields: item code, category/group, effective date, schedule/payment fields and
  provenance metadata; current-release XML is preferred over TXT where both represent the same release.
- Descriptor-only row treatment: `retain-local-only` unless redistribution terms explicitly permit it
- Payment fields permitted: schedule fee and permitted benefit/payment fields, labelled as schedule or benefit values
- Restrictions and evidence: raw XML/TXT remains ignored; exact source URL, release, retrieval time,
  byte count, checksum, parser transformation and source terms must accompany every derived bundle.

## Required confirmations

- [ ] Raw TXT files remain untracked.
- [ ] The two source checksums match the derived bundle validation report.
- [ ] Descriptor redistribution is explicitly addressed.
- [x] Scope decision is recorded in `conductor/DECISION_LOG.md`; checksum-bound artefact decisions
  remain required for each acquired publication candidate.
