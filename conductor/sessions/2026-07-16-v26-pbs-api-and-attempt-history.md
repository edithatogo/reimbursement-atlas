# 2026-07-16 v26 — PBS API discovery and acquisition evidence preservation

## Findings

- Official PBS documentation identifies the API as the monthly JSON/CSV distribution mechanism.
- The official Department of Health API catalogue exposes the active v3 server, OpenAPI export,
  required `Subscription-Key` header, and `/schedules`, `/items`, and `/fees` operations.
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
- The source registry now carries only the PBS credential environment-variable name. The
  downloader fail-closes with `blocked_secret` when it is absent and redacts the runtime header
  from stored command provenance when it is present. Added tests for both paths.
- Local network acquisition reached the official v3 API using the public portal access path: the
  July 2026 published schedule was selected by effective date, the 14,840-row items extract was
  retrieved across two pages, and the 17-row fees extract was retrieved. Raw files remain in the
  ignored local cache; no key or raw payload is tracked.
- The executable source record now targets the canonical `/schedules` endpoint rather than the
  documentation page, so the generated authenticated plan has the correct runtime behaviour.
- Redacted local checksums for the ignored raw acquisition are recorded here for handoff only:
  `schedules` 2f9d25172ce0503fedc01b1fc6aebeca5cd3bc6d6c34dcbeecd7cb51512ed5a9,
  `items` page 1 1bd0e95f100c015f39ee8ef8ab006998a1f63f347b52bcd2aec32c7efb1f9223,
  `items` page 2 e2aa5f7cc9a1c642d483b5457e9f1086c650490d6dd47152e82eb54046866733,
  and `fees` 3b080b57d4b8d70752cab0c4ca04ec89990b9279f8a20981cff4618439f84e06.

## Boundary

The PBS extract is locally acquired but remains review-pending because human licence/field review
has not been completed. No evidence-release or publication claim is made.
