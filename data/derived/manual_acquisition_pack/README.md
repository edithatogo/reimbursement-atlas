# Manual acquisition pack

This folder turns exact source-file records into a reviewed download checklist.
Raw files should remain under `data/raw_live/`, which is ignored by git.

```json
{
  "licence_gate_counts": {
    "metadata_only": 1,
    "public_reuse_review": 4,
    "restricted_or_licence_review": 2
  },
  "raw_handling_counts": {
    "local_raw_only": 2,
    "metadata_only": 5
  },
  "step_count": 7
}
```

## Workflow

1. Review the source URL and licence gate for each row.
2. Save permitted raw files to the suggested local path.
3. Run the snapshot command before parsing.
4. Parse into derived rows and run the public-data policy check.

## Steps

### step_001: MBS 20260701 item map TXT

- Source file id: `au_mbs_20260701_imap_txt`
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990fca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_IMAP.TXT
- Raw handling: `local_raw_only`
- Suggested local path: `data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT`

### step_002: MBS 20260701 item descriptors TXT

- Source file id: `au_mbs_20260701_desc_txt`
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990fca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_DESC.TXT
- Raw handling: `local_raw_only`
- Suggested local path: `data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT`

### step_003: CMS 26CLABQ3 file page

- Source file id: `us_cms_clfs_26clabq3_page`
- URL: https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files/26clabq3
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_clfs/26CLABQ3 landing page`

### step_004: CMS 26CLABQ3 AMA-gated ZIP

- Source file id: `us_cms_clfs_26clabq3_ama_zip`
- URL: https://www.cms.gov/license/ama?file=/files/zip/26clabq3.zip
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_clfs/26clabq3.zip`

### step_005: PBS API v3 documentation and CSV distribution

- Source file id: `au_pbs_api_v3_documentation`
- URL: https://data.pbs.gov.au/document/91327.html
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/au_pbs/PBS API/CSV endpoints`

### step_006: CMS ASP July 2026 payment-limit files page

- Source file id: `us_cms_asp_july_2026_payment_limit_page`
- URL: https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_asp/July 2026 ASP payment-limit files`

### step_007: CMS PFS RVU26C relative value files page

- Source file id: `us_cms_pfs_rvu26c_page`
- URL: https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_pfs/RVU26C relative value files`
