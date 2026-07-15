# v27 PBS acquisition evidence

Date: 2026-07-16

## Implemented

- Added `PbsApiAcquisitionRecord` and JSON schema export.
- Added `pbs_api_evidence` validation for schedules JSON, paginated items CSV and fees CSV.
- Added `pixi run pbs-acquisition-evidence`, which preserves tracked metadata when ignored raw
  inputs are absent and never writes raw content to tracked paths.
- Added source-specific required-column, invalid-row, count, byte-size and SHA-256 checks.
- Added publication-manifest, research-package, data-dictionary and dashboard exports.
- Added Conductor backlog/roadmap linkage and one deduplicated generated GitHub issue.

## Local evidence

- `schedule_code=4706`, effective date `2026-07-01`.
- 13 schedule rows, 10,000 item rows on page 1, 4,840 item rows on page 2 and 17 fee rows.
- All four endpoint records have `schema_status=pass` and `invalid_row_count=0`.
- Raw payloads remain under ignored `data/raw_live/au_pbs/`; tracked evidence contains no raw rows,
  credentials or absolute local paths.

## Gates

- 230 tests passed with 90.07% coverage.
- Ruff, basedpyright, Bandit, compileall and Astro dashboard build passed.
- Release readiness: 35/35 gates passed; repository release-ready remains distinct from evidence,
  research-publication, OSF and policy-claim readiness.

## Remaining review

Human source/licence/domain review is still required before the PBS extract can become a reviewed
bundle or support a policy claim. The authoritative issue remains GitHub issue #25.
