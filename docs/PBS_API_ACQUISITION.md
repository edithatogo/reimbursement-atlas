# PBS API acquisition

The PBS documentation confirms that the API is the current distribution mechanism for the
Schedule, is updated monthly, exposes JSON and CSV responses, and uses a shared public rate
limit. The documentation page is not a data extract.

## Access decision

The PBS public API documentation says that no user login is required, but the current API
gateway still requires a `Subscription-Key` header. An unauthenticated request to the official
v3 `/schedules` route returned HTTP 401 on 2026-07-18 with the gateway message that a
subscription key must be supplied. This repository does not mislabel the API as keyless and
does not attempt to bypass the gateway.

The API supports JSON and CSV responses and is explicitly intended for users to download and
store local copies. The current PBS Downloads page also lists a monthly "PBS API CSV files"
ZIP for users who do not need API functionality. XML and text files have been discontinued.
The operational policy is:

1. If `PBS_API_SUBSCRIPTION_KEY` is available, refresh the ignored local dataset through the
   official API and record redacted evidence.
2. If the key is unavailable but a non-empty ignored PBS cache already exists, reuse that
   dataset for validation and analysis, record `local_cache_available`, and leave API refresh
   available for a later credentialed run.
3. If the current PBS Downloads page exposes a public API-CSV ZIP, it may be downloaded into
   ignored local storage and validated as a dataset fallback. The URL must be discovered from
   the current official page, not guessed from a historical filename.
4. If neither API credential, current CSV ZIP, nor local cache is available, record
   `blocked_secret`; do not fabricate a download or claim that the current dataset was refreshed.

## Current probe

The official Department of Health API catalogue publishes a `Subscription-Key` for unregistered
public users. On 2026-07-16, using the current catalogue value at runtime and the JSON media type,
the public route returned HTTP 200 with 10 schedule records:

```text
https://data-api.health.gov.au/pbs/api/v3/schedules
Accept: application/json
```

The official Department of Health API catalogue now provides the exact v3 details:

- API server: `https://data-api.health.gov.au/pbs/api/v3`
- OpenAPI export: `https://data-api-portal.health.gov.au/developer/apis/pbs-api-public-v3?export=true&api-version=2022-04-01-preview`
- Required header: `Subscription-Key`
- Relevant operations: `/schedules`, `/items`, and `/fees`
- Response formats: `application/json` and `text/csv`
- Current public dataset alternative: PBS Downloads page "PBS API CSV files" ZIP
- Legacy status: XML and text files discontinued from 1 May 2026

The OpenAPI export is documentation metadata only. The current public-user key is displayed by
the catalogue and may rotate; copy it at runtime rather than storing it in the repository. It
must never be committed, printed, embedded in generated download plans, or written to provenance.

## Effective-date join and safe acquisition sequence

The `/items` and `/fees` extracts carry `schedule_code`; the effective date is authoritative in
the `/schedules` response. The parser contract must therefore join item/fee rows to the selected
schedule record by `schedule_code` before deriving an `effective_date`. It must not require an
`effective_date` column in every endpoint CSV.

1. Open the [official PBS API catalogue](https://data-api-portal.health.gov.au/apis), select
   `PBS API PUBLIC - v3`, and copy the displayed subscription key for unregistered public users.
2. Export it only for the acquisition process:

   ```bash
   export PBS_API_SUBSCRIPTION_KEY='(paste the current catalogue value here)'
   ```

3. Use the catalogue's current v3 server and OpenAPI export above; do not infer endpoint paths
   from an older v2 integration.
4. Fetch the `schedules` endpoint first and select a published monthly `schedule_code`; do not
   assume the largest code is the latest schedule.
5. Fetch only the reviewed endpoint set, respecting the API's published rate limit and inspecting
   `X-Rate-Limit-Remaining` and `X-Rate-Limit-Limit` response headers.
6. Store raw responses only under ignored `data/raw_live/au_pbs/`.
7. If using the official PBS API CSV ZIP, record the page URL, download URL, archive checksum,
   extracted endpoint checksums, and schedule-code join evidence.
8. Run source validation, source contracts and `parse_pbs_csv` against a reviewed CSV/JSON
   extract, then commit derived rows and redacted checksums only.

The source registry names `PBS_API_SUBSCRIPTION_KEY` as the runtime environment variable. The
acquisition helper returns a redacted `blocked_secret` attempt when it is absent; when present,
the value is passed only to the child HTTP process and is removed from command provenance.

## Local acquisition observation

The July 2026 published schedule was selected as `schedule_code=4706` from `effective_date`.
The ignored local cache contains the complete 14,840-row `/items` extract across two CSV pages
and the 17-row `/fees` extract for that schedule. These files are acquisition evidence only:
they remain outside Git, and no parser, reviewed bundle, evidence claim, or publication output is
treated as complete until human field and licence review is recorded.

The public API credential path is now executable, and the local-cache fallback prevents a
missing key from invalidating an already acquired dataset. The implementation remains
fail-closed at the monthly-extract field/licence-review step. GitHub issue
[#25](https://github.com/edithatogo/reimbursement-atlas/issues/25)
tracks the reviewed extract and licence decision.

## Latest governed acquisition evidence

The source-health workflow [29551222886](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29551222886)
ran with the GitHub Actions secret and acquired 10 schedule records, 14,840 item records across
two pages, and 17 fee records. Source validation and source-contract validation passed for the
three PBS endpoint classes. This is acquisition evidence, not licence or human review approval.

## Redacted acquisition evidence

When the ignored local cache is available, run:

```bash
pixi run pbs-acquisition-evidence
```

The command validates the cached schedules, item pages and fees responses and writes only
`data/derived/source_downloads/pbs_api_acquisition.*`. The tracked rows contain endpoint,
schedule, effective date, page, record count, required/observed columns, byte size, SHA-256,
and an explicit `acquired_unreviewed` status. They never contain raw response fields or an
absolute local path. CI preserves the existing metadata-only evidence when the ignored cache is
absent, so deterministic regeneration does not require credentials or raw payloads.

## 2026-07-18 access-mode recheck

The official v3 route was probed without a credential and returned HTTP 401. The official PBS
Downloads page now lists a public monthly PBS API CSV ZIP as the non-API alternative, while
confirming that XML and text files have been discontinued. The repository therefore keeps both
the subscription-key API path and a page-discovered CSV-ZIP fallback, with an existing ignored
cache as the final offline fallback.

## 2026-07-17 local runtime recheck

The current public-user key was read from the rendered official catalogue page and supplied only
to the local acquisition process. The July 2026 `/schedules` response, existing `/items` pages
and `/fees` response were retained only under ignored `data/raw_live/au_pbs/`. Redacted provenance
records 10 schedule records, 14,840 item records across two pages and 17 fee records, for 14,867
total PBS records. The key is absent from tracked files, generated commands and provenance.
Source validation and source-contract checks have zero blocking failures; the extract remains
`acquired_unreviewed` pending accountable licence and field review.
