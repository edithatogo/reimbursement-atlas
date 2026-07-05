#!/usr/bin/env bash
set -euo pipefail

mkdir -p data/raw_live/au_mbs && curl -L --fail --retry 3 -o data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990fca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_IMAP.TXT
mkdir -p data/raw_live/au_mbs && curl -L --fail --retry 3 -o data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990fca25692100069854/1bc94358d4f276d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_DESC.TXT
mkdir -p data/raw_live/au_pbs && curl -L --fail --retry 3 -o data/raw_live/au_pbs/PBS_API_CSV_endpoints https://data.pbs.gov.au/document/91327.html
