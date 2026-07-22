# Source licence evidence

This file records authoritative source-term observations used by the repository's conservative
licence gates. It is evidence for review, not a legal opinion or a blanket redistribution grant.

## Australian MBS

- Source: [MBS Online copyright information](https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/copyright)
- Rechecked: 2026-07-17
- Observation: the page states that material is Commonwealth copyright; limited personal,
  non-commercial, unaltered use is permitted; reproduction must retain the copyright and
  disclaimer notices; redistribution or commercial use requires prior written approval.
- Repository decision: keep raw MBS files in ignored local storage; the repository owner has
  approved the current checksum-bound derived/metadata scope with attribution and restrictions.
  This does not approve raw-file redistribution, descriptor redistribution, or broader use.
- Consequence: the source is public to access but is not treated as an open redistribution
  licence. Apache-2.0 applies to project-owned code and documentation only.

## Historical MBS archive boundary

- Archive index: [MBS Online downloads](https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/downloads)
- Historical index: [MBS Online 2010 to 2019](https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/MBSOnline-2010)
- Older index: [MBS Online previous downloads](https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/Prev-Downloads)
- Rechecked: 2026-07-17
- Observation: the official downloads page exposes current item-map and descriptor files and
  points to historical indexes; it does not convert the copyright notice into an open licence.
- Repository decision: retain the 343-target historical inventory as metadata-only and
  `manual_review_only`; the owner-approved scope applies to recorded derived/metadata
  candidates, not unreviewed historical payloads or broader redistribution.

## Australian PBS API

- Source: [Department of Health API catalogue](https://data-api-portal.health.gov.au/apis) and
  [PBS API developer information](https://data.pbs.gov.au/api/pbs-api.html)
- Accessed: 2026-07-16
- Observation: the current acquisition route is an authenticated API surface with subscription
  key access. The official API documentation states that the public data mart retains thirteen
  months of schedules, including the most recent schedule; this is a rolling retention window,
  not a historical archive. The repository has not inferred redistribution permission from API
  availability.
- Repository decision: keep `PBS_API_SUBSCRIPTION_KEY` runtime-only, never log or commit it, and
  keep acquisition and publication blocked until the key, field scope, terms and reviewed
  monthly extract are documented. Preserve any monthly history only in ignored local storage
  after review; do not represent the API's rolling window as historical coverage.

## Review boundary

The source registry, source-contract reports, publication manifest and checksum-bound licence
queue must agree before any derived source rows move from review to publication. The owner
approval is recorded in `data/licence_review/decisions.jsonl` for the exact current checksums;
source-content, domain, evidence and release gates remain separate and are not silently cleared.
