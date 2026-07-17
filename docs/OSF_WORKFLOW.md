# OSF workflow

Release snapshot described by this workflow record is
`4693b32113b97868083ecf86d9fd8ae09dfa2e1b` (2026-07-18). The checked-out `main` tip may be
newer; no OSF monitor evidence is implied for a newer commit.
The latest merged-main monitor refresh is run `29595536363`. Pinned
`osf-cli-go v1.0.0` discovery and the component plan passed; provisioning,
registration, upload and publication were skipped. The private
`Reimbursement Atlas` project remains a reusable target, but protocol, licence,
methods and governance approval are still required before mutation.

OSF is the planned home for research protocols, detailed reports, appendices and preprint staging. GitHub remains the implementation repository. Hugging Face hosts licence-safe derived datasets and the dashboard.

Historical monitor snapshots below are retained for auditability. They are not current
repository state; use this header and `data/derived/protocols/summary.json` as the source of
truth.

Generated artefacts:

- `data/derived/osf/component_plan.*`
- `data/derived/osf/osf_publication_manifest.json`
- `data/derived/osf/preprint_checklist.md`
- `data/derived/osf/sync_manifest.jsonl`
- `data/derived/osf/registration_review_packet.md`
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

The automation pins stable `osf-cli-go` at `v1.0.0` and verifies both the embedded Go module version and the unauthenticated command contract with `pixi run osf-cli-contract`. The OSF plan job installs the official SHA-pinned Pixi action before invoking that contract, so CI does not depend on a preinstalled runner executable. The release includes machine-readable output, node export, metadata validation, storage upload and registration commands. The repository's checksum-based reconciliation layer remains the manifest adapter: it compares desired and remote state before any CLI mutation, and every row remains `publish_allowed: false` until accountable human review changes the publication decision. CI must not emulate idempotency with destructive ad hoc shell logic.

### Local CLI contract check

Do not rely on an unrelated or older `osf` executable already on `PATH`. Install the
repository-pinned binary into an ignored temporary or user bin directory, then pass it
explicitly:

```bash
GOBIN="${TMPDIR:-/tmp}/reimbursement-atlas-bin"
mkdir -p "$GOBIN"
GOBIN="$GOBIN" go install github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0
OSF_BIN="$GOBIN/osf" pixi run osf-cli-contract
```

The contract probe is unauthenticated and read-only. It must pass before any credentialed
OSF workflow is considered runnable. The local `osf` executable may belong to an older CLI
release and is intentionally not accepted as evidence for the pinned workflow.

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

The idempotent provisioning check in workflow run `29460182675` returned `created: false` for
private project `q8cnx`. This confirms the configured project is reusable without creating a
duplicate; no OSF mutation occurred.

See `docs/reviews/SIMULATED_MULTI_AGENT_PROTOCOL_REVIEW_2026-07-11.md` for the advisory review and unresolved human gates.

## Latest read-only discovery

Workflow run `29475141289` on merged main commit `e8b8a2e` repeated the pinned CLI
discovery and OSF plan. Discovery succeeded for the configured private
`Reimbursement Atlas` project (`q8cnx`); provisioning and publication jobs were skipped.
The plan verified `osf-cli-go` `v1.0.0` and the fail-closed sync manifest. No OSF node,
registration, file or project metadata was mutated.

OSF workflow run `29473382425` on `main` successfully ran the pinned CLI discovery path and
the OSF plan. It found the expected private `Reimbursement Atlas` project (`q8cnx`);
provisioning, registration, upload and publication were not performed. The sanitized project
listing remains available only as a seven-day private workflow artifact, not as a tracked
repository file. The sync-manifest check passed with every row fail-closed, so this evidence
does not grant publication approval.

The workflow uses `osf-cli-go` `v1.0.0`; the pinned binary was installed into an ignored
temporary directory on 2026-07-17 and the local contract passed with
`OSF CLI contract passed: osf 1.0.0`. An unrelated `osf` `0.3.2` executable on the
workstation is not used as workflow evidence. This validates the toolchain only; it does
not authorize OSF registration or publication.

The historical merged repository state referenced by the earlier preflight was `c186e54` (`main`).
The latest remote discovery evidence above is retained as a read-only preflight record; no OSF
mutation occurred. The contract task now refuses ambiguous `PATH` lookup and requires `OSF_BIN` or
`--binary`, preventing an unrelated older `osf` executable from being mistaken for the pinned
official CLI.

The latest read-only refresh on `main` (`c7a55b3e4483265ffe60637714e930512ec22cdb`) was
workflow run `29517248071`: discovery and the OSF component plan passed, provisioning and
publication were skipped, and no OSF project, node, registration or file was mutated.

The current read-only refresh on merged `main` (`9476628`) was workflow run
`29545432007`. The pinned CLI discovery succeeded and found 28 accessible projects, including the
private `Reimbursement Atlas` project `q8cnx`; the OSF component plan and fail-closed sync-manifest
check also passed. Provisioning, registration, upload and publication were skipped, and no OSF
project, node, registration or file was mutated. The sanitized project listing remains a temporary
workflow artifact and no token or project payload is tracked.

The latest refresh on merged `main` (`7a6b03f`) was workflow run
`29551589259`. The pinned `osf-cli-go` v1.0.0 discovery and component-plan jobs passed, and the
private `Reimbursement Atlas` project `q8cnx` was accessible. Provisioning, registration, upload
and publication were skipped; no OSF project, node, registration or file was mutated.

The current read-only refresh on merged `main` (`c2cdea7`) was workflow run
[29565049272](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29565049272).
The pinned `osf-cli-go` v1.0.0 discovery returned 28 accessible projects and found the existing
private `Reimbursement Atlas` project `q8cnx`. Provisioning, registration, upload and publication
were skipped; no OSF project, node, registration or file was mutated.

The latest read-only refresh on merged `main` (`fa5b042`)
([29567562072](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29567562072))
passed both OSF discovery and the component-plan job. Discovery again returned 28 accessible
projects and the private `Reimbursement Atlas` project `q8cnx`; provisioning, registration,
upload and publication were skipped. The sanitized discovery artifact was retained only as a
short-lived workflow artifact, and no OSF project, node, registration, file or token-bearing
payload was mutated or committed.

The repository is now at merged commit `db367f4`. No newer OSF workflow has been run on that
commit; the successful `29567562072` result above is therefore the latest operational OSF
evidence, not evidence of a new registration or publication. Registration, upload and
publication remain skipped until the protocol, licence, evidence and governance gates pass.

The current merged-main refresh on `fc47649` is workflow run
[29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259).
Pinned `osf-cli-go v1.0.0` discovery and the component plan passed; the sanitized artifact
contained 28 accessible projects and the private `Reimbursement Atlas` project `q8cnx`.
Provisioning, registration, upload and publication were skipped, and no OSF mutation occurred.

The latest current-main refresh is workflow run
[29571893420](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571893420).
Pinned `osf-cli-go v1.0.0` discovery found 28 accessible projects and the private
`Reimbursement Atlas` project `q8cnx`; provisioning, registration, upload and publication
were skipped. The sanitized discovery artifact contained no token-bearing fields.
