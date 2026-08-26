# Implementation plan

- [x] SEC-A-01: Validate read-only GitHub security-settings monitor behavior.
- [x] SEC-A-02: Validate history-secret, workflow and branch-protection checks.
- [x] SEC-A-03: Reconcile generated security issue and Project projections.
- [x] Review Fixes: Keep unavailable account-level controls blocked rather than
  reporting compensating controls as equivalent.
- [x] SEC-A-04: Obtain and verify account-level GitHub security settings with
  sufficient repository permissions.

The owner-authenticated API confirms secret scanning and push protection are
enabled. GitHub leaves non-provider patterns and validity checks disabled for
this repository after an authenticated enable request; this remains an
account-level capability blocker rather than an unresolved observation.

## Closeout

- [x] Archive the track after all repository-owned controls pass and preserve
  the account-capability limitation as monitored external state rather than an
  unbounded implementation task.
- [x] Reconcile the completed archive marker, registry phase and metadata while
  preserving optional account controls as non-required external observations.
  (Issue #759)
