# 2026-07-16 v26 — PBS API discovery and acquisition evidence preservation

## Findings

- Official PBS documentation identifies the API as the monthly JSON/CSV distribution mechanism.
- The candidate public route `https://data-api.health.gov.au/pbs/api/v3/schedules?format=json`
  returned HTTP 401 because a subscription key is required.
- The documentation page is not a monthly data extract; no PBS raw response was retained.
- GitHub issue #25 was updated with the official documentation links and the exact prerequisite.

## Implementation

- Source registry and validation playbook now record the subscription-key and Swagger-resolution
  prerequisites.
- `docs/PBS_API_ACQUISITION.md` defines the safe schedule-code-first acquisition sequence.
- Plan-only regeneration now preserves existing `download_attempts` evidence. Explicit attempt
  runs still write a fresh attempt snapshot.
- Added a unit test covering preservation of historical attempt records.

## Boundary

The PBS monthly extract remains pending because the external subscription key, current Swagger
request URL and human licence/field review are not available in the local environment.
