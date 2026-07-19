# CMS PFS Review Decision

Use this form for issue [#27](https://github.com/edithatogo/reimbursement-atlas/issues/27).

## Candidate

- Source: CMS RVU26C relative-value files
- Repository state: landing-page metadata and synthetic parser fixture only

## Reviewer decision

- Reviewer: `repository-owner`
- Reviewed at: `2026-07-19`
- Decision: `approved` for restricted numeric RVU/payment-derived fields; no CPT descriptor redistribution
- CMS terms URL:
- Attribution text:
- Allowed numeric RVU/payment fields: RVUs and permitted payment inputs with locality and conversion-factor metadata
- HCPCS/CPT identifiers permitted: `conditional`, subject to source terms
- Descriptor fields prohibited: CPT descriptors and descriptor-derived text
- Conversion-factor/locality caveats: RVUs are not national prices; derived payment values must retain locality and conversion-factor context
- Evidence/reference: user scope approval recorded in `conductor/DECISION_LOG.md`; exact file review remains pending
