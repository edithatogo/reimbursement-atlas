# Source download hardening

The atlas should be able to fetch public source files with `curl`, `wget`, or API clients, but only after the relevant source-file record has passed the licence and raw-data gates.

## v15 hardening

`reimbursement-atlas source-download-plan` now emits shell-safe commands with:

- `curl -L --fail` for redirect/error handling;
- five retries with `--retry-all-errors`;
- connection and total download timeouts;
- resume support using `--continue-at -`;
- sidecar HTTP headers using `--dump-header`;
- ETag cache sidecars using `--etag-save` and `--etag-compare`;
- shell quoting for paths and URLs;
- API `Accept` headers for `api_rate_limited` records;
- refusal to automate landing pages, licence click-through records, metadata-only rows or restricted records.

Raw payloads remain under ignored local paths such as `data/raw_live/`. Derived metadata and command plans may be committed, but raw files and raw descriptors should not be committed.

## Typical workflow

```bash
PYTHONPATH=src reimbursement-atlas source-download-plan --method curl
bash data/derived/source_downloads/download_commands.sh
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
```

If the environment cannot resolve a host or reach the internet, `--attempt` records `blocked_network` rather than treating the source as missing.

## Next improvements

- Add source-specific content validation once real files are downloaded.
- Add checksum pinning for known source releases after human review.
- Add a `source diff` command to compare two reviewed source versions.
- Add source-page monitoring that opens a GitHub issue when a listed file changes.
