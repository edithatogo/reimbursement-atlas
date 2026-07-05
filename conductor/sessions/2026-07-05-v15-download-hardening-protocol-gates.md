# Session: v15 source-download hardening and protocol gates

Date: 2026-07-05

## Focus

Implemented two practical hardening layers before live-source ingestion:

1. Hardened source download plans with retries, resume support, shell quoting, header/ETag sidecars and licence-gate refusal.
2. Protocol-status generation so OSF-aligned research questions have completeness evidence and actionable next steps.

## Generated artefacts

- `data/derived/source_downloads/download_plans.*`
- `data/derived/protocols/protocol_status.*`
- `data/derived/protocols/summary.json`
- dashboard copies under `apps/dashboard/public/data/`
- updated publication manifest and seed-lake tables

## Next recommended implementation

- Run the download commands in a network-enabled environment.
- Add source-specific content validators after the first real MBS/CMS/PBS files are available.
- Expand protocol templates for specific methods, including crosswalk adjudication and sensitivity analysis plans.
