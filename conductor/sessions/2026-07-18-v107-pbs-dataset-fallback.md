# Session: PBS API and dataset fallback

## Decision

The PBS public API documentation says no user login is required, but the current API gateway
requires a `Subscription-Key` header. A credential-free probe of the official v3 `/schedules`
route returned HTTP 401. The official material describes JSON and CSV API responses that users
can save locally; the separate PBS API CSV publication is under the embargo section.

## Implementation

- Kept `PBS_API_SUBSCRIPTION_KEY` as an ephemeral runtime credential for API refresh.
- Added `local_cache_available` when a non-empty ignored target already exists and the key is
  absent. The raw dataset remains local-only and the API remains available for later refresh.
- Kept `blocked_secret` when neither credential nor local cache is available.
- Added regression coverage and updated the PBS acquisition contract and source registry notes.

## Review boundary

The local dataset remains `acquired_unreviewed` until the accountable PBS licence and field review
is recorded. This change does not authorize raw payload tracking or public publication.
