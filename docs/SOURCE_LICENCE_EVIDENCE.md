# Source licence evidence

This file records authoritative source-term observations used by the repository's conservative
licence gates. It is evidence for review, not a legal opinion or a blanket redistribution grant.

## Australian MBS

- Source: [MBS Online copyright information](https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/copyright)
- Rechecked: 2026-07-17
- Observation: the page states that material is Commonwealth copyright; limited personal,
  non-commercial, unaltered use is permitted; reproduction must retain the copyright and
  disclaimer notices; redistribution or commercial use requires prior written approval.
- Repository decision: keep raw MBS files in ignored local storage; keep the July 2026 derived
  pair bundle as `public_reuse_review`; do not publish the bundle or descriptor-derived fields
  until an accountable reviewer records the applicable permission and attribution.
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
  `manual_review_only`; do not mirror historical payloads until each target's terms and intended
  derived fields are reviewed.

## Australian PBS API

- Source: [Department of Health API catalogue](https://data-api-portal.health.gov.au/apis) and
  [PBS API developer information](https://data.pbs.gov.au/api/pbs-api.html)
- Accessed: 2026-07-16
- Observation: the current acquisition route is an authenticated API surface with subscription
  key access. The repository has not inferred redistribution permission from API availability.
- Repository decision: keep `PBS_API_SUBSCRIPTION_KEY` runtime-only, never log or commit it, and
  keep acquisition and publication blocked until the key, field scope, terms and reviewed
  monthly extract are documented.

## Review boundary

The source registry, source-contract reports, publication manifest and checksum-bound licence
queue must agree before any derived source rows move from review to publication. A maintainer
or domain/licensing reviewer must record the source terms, permitted fields, attribution,
redistribution decision, reviewer and date in the accountable review process.
