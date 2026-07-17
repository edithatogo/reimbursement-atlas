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

## Current acquisition observation

On 2026-07-17, the hardened `curl` attempt revalidated both July 2026 MBS TXT
files and the PBS v3 schedules response into ignored local raw storage. Six other
targets remain intentionally skipped behind source/licence review. The PBS API
runtime key was read from the official catalogue for this invocation only; it was
not persisted, logged or committed. The current local source-health result is
`review_required` with zero operational blockers and six licence-review targets.
The authoritative current status is generated in
`data/derived/source_health/acquisition_status.json`.

The credentialed GitHub Actions source-health run on merged `main`
([29571899135](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571899135))
completed with `review_required`: it schema-validated 14,867 PBS records and left all
raw payloads in runner/local-only storage. The local rerun now reaches the same
review-required boundary without retaining the key.
