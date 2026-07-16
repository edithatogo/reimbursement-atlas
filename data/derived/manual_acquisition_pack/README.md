# Manual acquisition pack

This folder turns exact source-file records into a reviewed download checklist.
Raw files should remain under `data/raw_live/`, which is ignored by git.

```json
{
  "licence_gate_counts": {
    "metadata_only": 3,
    "public_reuse_review": 4,
    "restricted_or_licence_review": 2
  },
  "raw_handling_counts": {
    "local_raw_only": 2,
    "metadata_only": 7
  },
  "step_count": 9
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
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_IMAP.TXT
- Raw handling: `local_raw_only`
- Suggested local path: `data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT`

### step_002: MBS 20260701 item descriptors TXT

- Source file id: `au_mbs_20260701_desc_txt`
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_DESC.TXT
- Raw handling: `local_raw_only`
- Suggested local path: `data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT`

### step_003: MBS 2010 to 2019 archive downloads page

- Source file id: `au_mbs_2010_2019_downloads_page`
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/MBSOnline-2010
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/au_mbs/MBSOnline-2010`

### step_004: MBS 1989 to 2010 previous downloads page

- Source file id: `au_mbs_1989_2010_previous_downloads_page`
- URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/Prev-Downloads
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/au_mbs/Prev-Downloads`

### step_005: CMS 26CLABQ3 file page

- Source file id: `us_cms_clfs_26clabq3_page`
- URL: https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files/26clabq3
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_clfs/26CLABQ3 landing page`

### step_006: CMS 26CLABQ3 AMA-gated ZIP

- Source file id: `us_cms_clfs_26clabq3_ama_zip`
- URL: https://www.cms.gov/license/ama?file=/files/zip/26clabq3.zip
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_clfs/26clabq3.zip`

### step_007: PBS public API v3 schedule and item endpoints

- Source file id: `au_pbs_api_v3_documentation`
- URL: https://data-api.health.gov.au/pbs/api/v3/schedules
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/au_pbs/pbs_v3_schedules.json`

### step_008: CMS ASP July 2026 payment-limit files page

- Source file id: `us_cms_asp_july_2026_payment_limit_page`
- URL: https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_asp/July 2026 ASP payment-limit files`

### step_009: CMS PFS RVU26C relative value files page

- Source file id: `us_cms_pfs_rvu26c_page`
- URL: https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files
- Raw handling: `metadata_only`
- Suggested local path: `data/raw_live/us_cms_pfs/RVU26C relative value files`
