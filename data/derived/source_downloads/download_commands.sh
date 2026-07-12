#!/usr/bin/env bash
set -uo pipefail

failures=0
if (mkdir -p data/raw_live/au_mbs && curl -L --fail --retry 5 --retry-all-errors --connect-timeout 20 --max-time 180 --create-dirs --dump-header data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT.headers --etag-save data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT.etag --etag-compare data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT.etag -o data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_IMAP.TXT); then
  :
else
  code=$?
  printf '%s\n' 'download command 1 failed with exit code ' "$code" >&2
  failures=$((failures + 1))
fi
if (mkdir -p data/raw_live/au_mbs && curl -L --fail --retry 5 --retry-all-errors --connect-timeout 20 --max-time 180 --create-dirs --dump-header data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT.headers --etag-save data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT.etag --etag-compare data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT.etag -o data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990d3ca257ccf0000aa73/%24FILE/20260701_MBSONLINE_DESC.TXT); then
  :
else
  code=$?
  printf '%s\n' 'download command 2 failed with exit code ' "$code" >&2
  failures=$((failures + 1))
fi
if (mkdir -p data/raw_live/au_pbs && curl -L --fail --retry 5 --retry-all-errors --connect-timeout 20 --max-time 180 --create-dirs --dump-header data/raw_live/au_pbs/PBS_API_CSV_endpoints.headers --etag-save data/raw_live/au_pbs/PBS_API_CSV_endpoints.etag --etag-compare data/raw_live/au_pbs/PBS_API_CSV_endpoints.etag --header 'Accept: application/json, text/csv;q=0.9, */*;q=0.1' -o data/raw_live/au_pbs/PBS_API_CSV_endpoints https://data.pbs.gov.au/document/91327.html); then
  :
else
  code=$?
  printf '%s\n' 'download command 3 failed with exit code ' "$code" >&2
  failures=$((failures + 1))
fi

if (( failures > 0 )); then
  printf '%s\n' "$failures download command(s) failed; inspect source validation and attempt metadata." >&2
  exit 1
fi
