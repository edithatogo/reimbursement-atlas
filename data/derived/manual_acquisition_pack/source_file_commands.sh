#!/usr/bin/env bash
set -euo pipefail

# Review URLs/licences manually before downloading. Do not commit raw files.

# step_001: MBS 20260701 item map TXT
# URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_IMAP.TXT
mkdir -p data/raw_live/au_mbs
# Snapshot: reimbursement-atlas snapshot-local-file --source-version-id au_mbs_20260701_txt_pair --content-type text/plain data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT
# Parse: # Bundle after both MBS TXT files are present: reimbursement-atlas reviewed-mbs-txt-pair-bundle data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT --output-dir data/derived/reviewed_sources/au_mbs_20260701_txt_pair

# step_002: MBS 20260701 item descriptors TXT
# URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_DESC.TXT
mkdir -p data/raw_live/au_mbs
# Snapshot: reimbursement-atlas snapshot-local-file --source-version-id au_mbs_20260701_txt_pair --content-type text/plain data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
# Parse: # Bundle after both MBS TXT files are present: reimbursement-atlas reviewed-mbs-txt-pair-bundle data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT --output-dir data/derived/reviewed_sources/au_mbs_20260701_txt_pair

# step_003: MBS 2010 to 2019 archive downloads page
# URL: https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/MBSOnline-2010
mkdir -p data/raw_live/au_mbs
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.

# step_004: CMS 26CLABQ3 file page
# URL: https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files/26clabq3
mkdir -p data/raw_live/us_cms_clfs
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.

# step_005: CMS 26CLABQ3 AMA-gated ZIP
# URL: https://www.cms.gov/license/ama?file=/files/zip/26clabq3.zip
mkdir -p data/raw_live/us_cms_clfs
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.

# step_006: PBS API v3 documentation and CSV distribution
# URL: https://data.pbs.gov.au/document/91327.html
mkdir -p 'data/raw_live/au_pbs/PBS API'
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.

# step_007: CMS ASP July 2026 payment-limit files page
# URL: https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files
mkdir -p data/raw_live/us_cms_asp
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.

# step_008: CMS PFS RVU26C relative value files page
# URL: https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files
mkdir -p data/raw_live/us_cms_pfs
# Snapshot: # Metadata-only record; review the landing page or endpoint before downloading.
# Parse: # No parser runs for metadata-only landing/API records.
