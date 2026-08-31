# Plan

- [x] Review #798, regenerate dashboard SBOM and downstream evidence, validate and merge.
- [ ] Review #799 against updated main, regenerate Python evidence, validate and merge.
- [ ] Review #800 against updated main, regenerate action inventory, validate and merge.
- [ ] Reconcile remaining #797 drift; retain incompatible TypeScript under #362.
- [ ] Renew hosted dashboard/provenance packets under standing scope after the
  dependency baseline settles; do not request fresh owner checksum approvals.
- [ ] Record validation, verify merged trees and clean merged branches before archive.

## Initial diagnosis

PR #798 changes Astro 7.2.3 to 7.2.4 and @astrojs/react 6.0.3 to 6.0.4.
Hosted run 33308373236 reports deterministic SBOM and downstream readiness,
research-package, source-drift and dashboard/seed-lake differences. No application
or security failure is reported by the other completed checks. Regenerate the
canonical evidence, not the approval records by hand.

PR #798 local validation: all 27 native `local-quality` gates passed, including
Python 3.14, coverage, typing, security, package build and dashboard build/audit.
Generated projections are refreshed using the hosted harness sequence. Protected
exact-head hosted checks passed. PR #798 merged as `9e5d082ed93a50747bcd7c19182691eccf08281a`;
tested and merged trees both equal `3013916d2c21b7f8989ea1156a66880df638fc6c`.
The merged local feature branch was removed; #799 and #800 remain separate pending work.
