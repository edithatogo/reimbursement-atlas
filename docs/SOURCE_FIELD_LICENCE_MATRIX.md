# Source Field Licence Matrix

This matrix separates permission to acquire or parse a source from permission to redistribute
derived fields. Blank or pending cells are not approval.

| Source | Candidate fields | Default public output | Excluded pending review | Required decision |
|---|---|---|---|---|
| PBS API v3 | `schedule_code`, schedule metadata, item identifiers, names, forms, programme and restriction indicators | Derived rows with source URL, schedule code, effective date, and explicit schedule/list-price labelling | Raw JSON/CSV, API headers, credentials, unreviewed restriction text, claims about net prices | [PBS review form](licence_decisions/PBS.md) |
| MBS July 2026 TXT pair | Joined item-map fields and permitted payment metadata | Derived-only joined rows after Commonwealth reuse review | Raw TXT, descriptor-only rows, unrestricted redistribution of descriptions | [MBS review form](licence_decisions/MBS.md) |
| CMS CLFS 26CLABQ3 | Numeric payment fields and source metadata if permitted | Numeric payment evidence only | CPT descriptors, descriptor-derived text, raw AMA-gated archive | [CMS CLFS review form](licence_decisions/CMS_CLFS.md) |
| CMS ASP July 2026 | Payment limits, effective date, NDC-HCPCS crosswalk fields if permitted | Payment-limit evidence, not coverage or net-price claims | Raw restricted files and unsupported coverage interpretations | [CMS ASP review form](licence_decisions/CMS_ASP.md) |
| CMS PFS RVU26C | Numeric RVUs and derived payment fields if permitted | Numeric fee evidence with locality/conversion-factor caveats | CPT descriptors and unsupported national-price claims | [CMS PFS review form](licence_decisions/CMS_PFS.md) |

## Decision rule

An approved source does not approve every field. Each reviewer must identify the allowed field
set, excluded field set, attribution, redistribution permission, restrictions, and evidence URL
in the corresponding form. The generated licence queue remains authoritative for checksums and
candidate artefact paths.
