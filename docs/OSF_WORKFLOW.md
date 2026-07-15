# OSF workflow

OSF is the planned home for research protocols, detailed reports, appendices and preprint staging. GitHub remains the implementation repository. Hugging Face hosts licence-safe derived datasets and the dashboard.

Generated artefacts:

- `data/derived/osf/component_plan.*`
- `data/derived/osf/osf_publication_manifest.json`
- `data/derived/osf/preprint_checklist.md`
- `data/derived/osf/sync_manifest.jsonl`
- `protocols/*.md`
- `reports/*.md`

Publication rules:

1. Upload protocols and reports before or alongside public releases.
2. Do not upload raw restricted source files unless a licence review explicitly permits it.
3. Use OSF components to separate protocols, reports, appendices, preprints and reproducibility packages.
4. Keep OSF publication token-gated and dry-run by default in CI.

## Registration lifecycle

Private OSF components may support collaborative drafting, but neither upload nor simulated review constitutes registration approval. Registration and public publication fail closed until signed methods, domain, licence and governance reviews are recorded and reviewed-source and source-contract gates pass.

1. Freeze protocol version, source cutoff, analysis manifest, code commit and expected outputs.
2. Record contributor roles, accountable approvers and signed decisions outside generated agent output.
3. Create an immutable registration only after approval; preserve its identifier and timestamp.
4. Record amendments, deviations and withdrawals without overwriting prior versions.
5. Apply embargo and access controls explicitly.
6. Verify remote hashes and component placement after upload; keep tokens outside files and logs.

The automation pins `osf-cli-go` at `v1.0.0-rc.1` and verifies the embedded Go module version. The sync manifest records local paths, target paths, sizes and SHA-256 values, but every row remains `publish_allowed: false` until accountable human review changes the publication decision. The current CLI does not yet provide manifest-native path reconciliation, so CI must not emulate idempotency with destructive ad hoc shell logic.

## Project discovery

The workflow supports a read-only `discover=true` dispatch. It uses the repository
`OSF_TOKEN` secret to list accessible projects with the pinned CLI and uploads only a
sanitized seven-day artifact containing project IDs, titles, descriptions and public
flags. It does not create, update or publish any OSF node. Use the discovered project ID
to configure the repository `OSF_PROJECT_ID` variable only after confirming the project
identity and protocol ownership.

The workflow also supports a token-gated `provision=true` dispatch. It searches the
authenticated account for the exact title `Reimbursement Atlas` and creates one private
project only when no exact match exists. The seven-day artifact contains only the
project ID, title, schema version and whether creation occurred. It does not configure
repository variables or upload research files; configure `OSF_PROJECT_ID` separately
only after checking the artifact and ownership.

See `docs/reviews/SIMULATED_MULTI_AGENT_PROTOCOL_REVIEW_2026-07-11.md` for the advisory review and unresolved human gates.
