# Data acquisition automation

The project now has an executable acquisition layer:

```bash
reimbursement-atlas source-download-plan
reimbursement-atlas source-download-plan --attempt --method curl
python scripts/make_source_download_plan.py --attempt --method wget
```

The downloader respects licence gates:

- landing pages and metadata-only records are not auto-downloaded;
- licence-clickthrough or restricted records are skipped;
- executable public file/API candidates are downloaded only into ignored local raw storage;
- every attempt is recorded in `data/derived/source_downloads/download_attempts.*`.

The generated `data/derived/source_downloads/download_commands.sh` launcher
delegates to the same `--attempt` path, so running the shell launcher also
writes attempt rows and local metadata sidecars instead of bypassing provenance.

In this sandbox, direct DNS resolution for `www.mbsonline.gov.au` and GitHub standalone Python downloads was blocked. The failure is recorded as a blocked network gate rather than silently ignored.
