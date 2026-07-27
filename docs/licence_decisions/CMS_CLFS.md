# CMS CLFS Review Decision

Use this form for issue [#24](https://github.com/edithatogo/reimbursement-atlas/issues/24).

## Candidate

- Source: CMS CLFS `26CLABQ3`, expected 2,206 records
- Access: AMA/CPT licence click-through
- Repository state: acquired locally on `2026-07-27`; raw payload remains ignored

## Reviewer decision

- Reviewer: `repository-owner`
- Reviewed at: `2026-07-19`
- Decision: `approved` for restricted numeric-derived fields; no CPT descriptor redistribution
- CMS/AMA terms URL: `https://www.cms.gov/license/ama?file=/files/zip/26clabq3.zip`
- Attribution text: CMS CLFS numeric payment data; CPT identifiers and descriptors excluded
- Local acquisition permitted: `yes`, subject to the source terms and manual licence flow
- Allowed numeric fields: permitted laboratory/payment values and source metadata
- HCPCS/CPT identifiers permitted: `conditional`, only where the applicable terms allow them
- Descriptor fields prohibited: CPT descriptors and descriptor-derived text
- Redistribution permission: derived numeric fields only after checksum-bound review
- Evidence/reference: source ZIP SHA-256 `3abf41e0c97068c8551055591db21d806fe20aa409eec9278e8e24891d463f1f`;
  extracted CSV SHA-256 `f5a090789c40fe791b478a735c7cf5399e86726adc788f11829435cb0ca4d7d5`;
  reviewed bundle `snapshot_us_cms_clfs_26clabq3_ama_zip_f5a090789c40`

Only the derived bundle may be published. The raw archive, CPT/HCPCS identifiers,
short descriptions, long descriptions and extended descriptions remain local and excluded.
