# Review Decisions

## Owner approval scope (2026-07-19)

The repository owner approves the non-paper recommendations: derived-only source
processing within the recorded licence restrictions, protocol/report staging,
dataset and dashboard publication preparation, mapping benchmark outcomes and
cross-platform review preparation. Paper, preprint and manuscript publication is
explicitly **not approved**. This authorization does not approve raw payload
redistribution, unsupported evidence or policy claims, or bypass the technical
OSF/Hugging Face credential, snapshot, destination and release gates.

This checklist is the human/external boundary for the current release candidate.
The repository owner has approved the current checksum-bound licence scope; future
checksum changes must still fail closed and require new explicit approval.

| Decision | Current state | Evidence | Unblock action |
| --- | --- | --- | --- |
| Code versus data licensing | decided | `docs/LICENSING.md`, `data/seed/source_registry.*` | Keep project code/documentation Apache-2.0; apply CMS/AMA and other provider terms to source data. |
| CMS CLFS/CPT fields | owner-approved bounded derived scope; source publication remains gated | `data/derived/source_contracts/source_contract_validation.jsonl`, `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md` | Retain only permitted numeric payment/RVU/locality/effective-date/source-version fields and provenance; exclude CPT/HCPCS descriptors, restricted crosswalks, raw files, credentials, coverage conclusions and net-price claims. Revalidate exact source terms before publication. |
| Mapping calibration | owner-approved protocol; current benchmark remains smoke-only and evidence gate remains review-required | `docs/MAPPING_CALIBRATION_PROTOCOL.md`, `data/mapping_review/decisions.jsonl`, `data/derived/vertical_slice/mapping_calibration_gate.json` | Build the source-stratified 750-case pack, complete blinded dual review and adjudication, then evaluate the untouched holdout before policy use. |
| OSF protocol package | owner-approved local-only non-paper staging; no remote mutation | `data/derived/osf/sync_manifest.jsonl`, [OSF workflow run 29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259) | Keep protocols, reports and research-package artefacts local; do not upload, register or publish while paper publication is excluded. |
| Hugging Face dataset/Space | destination metadata reconciled; publication remains gated | Hub API readback 2026-07-21: Space `c0dade5`, dataset `ef007dc` | Retain `license=other` for source-derived dataset content and Apache-2.0 for Space code; do not publish dataset payloads until licence, evidence, research and policy gates pass. |
| Zenodo DOI | owner-approved local-only archive; no deposit | `data/derived/release_readiness/summary.json`, [Zenodo preflight run 29569972301](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972301) | Retain the verified local bundle/archive and checksums; do not deposit or mint a DOI until evidence, licence, OSF and policy gates pass. |
| Historical MBS/PBS expansion | owner-approved metadata and local-cache scope; parsing/publication remain gated | `data/derived/final_handoff/final_handoff_tasks.jsonl`, `data/derived/historical_sources/summary.json` | Track catalogue metadata, URLs, dates, checksums and acquisition attempts; retain raw files only in ignored local storage; require source-specific reuse decisions before parsing or publication. |
| PBS public API acquisition | public-user key path validated; July 2026 schedule acquired unreviewed | `docs/PBS_API_ACQUISITION.md`, `data/derived/source_downloads/pbs_api_acquisition.jsonl`, GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25) | Copy the current public key from the official catalogue at runtime, fetch `/schedules` before `/items` and `/fees`, then review the selected monthly fields and source terms before promotion or publication. |
| July 2026 MBS TXT pair | bundle validated; current derived/metadata scope owner-approved; provider restrictions retained | `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/validation_report.json`, `docs/SOURCE_LICENCE_EVIDENCE.md`, issue [#23](https://github.com/edithatogo/reimbursement-atlas/issues/23) | Preserve attribution/notices and review descriptor-only rows before any evidence or public-release claim; no raw or broader redistribution is approved. |
| Dashboard visual baselines | owner-approved tested baseline; formal WCAG conformance not claimed | `docs/DASHBOARD_VALIDATION.md`, issue [#188](https://github.com/edithatogo/reimbursement-atlas/issues/188) | Retain the cross-browser automated evidence and re-review after material UI changes; automated axe/screenshot results remain scoped evidence, not a universal accessibility certification. |
| Artifact-level licence review | owner-approved scope; 194 checksum-bound decisions recorded and validated; 194 approved and 0 blocked | `data/licence_review/decisions.jsonl`; `data/derived/licence_review/`; `docs/LICENCE_DECISION_MATRIX.md` | Decisions apply only to the exact path/checksum and documented scope. Future checksum changes must be re-reviewed. Do not treat the total as a source-file count. |

Current local proof remains separate from these decisions: repository release readiness is
green, while evidence, policy-claim, research-publication and archival readiness remain
fail-closed.

The current decision file records `approved` for each exact candidate under the approved
derived/metadata scope. It does not approve raw payloads, restricted descriptors,
confidential values, unsupported claims, or any later checksum change.

## Grouped Owner Direction (2026-07-20)

The repository owner approved the grouped recommendations for the remaining pre-publication
gates:

- **Group A, source and licence scope:** historical MBS/PBS catalogue and local-cache work may
  proceed as metadata-first, with source-specific reuse review before parsing or publication;
  CMS CLFS work is limited to permitted derived numeric/payment fields and source metadata, with
  CPT/HCPCS descriptors, restricted crosswalks and raw AMA-gated payloads excluded.
- **Group B, mapping and evidence methodology:** retain the conservative human-review rule,
  preserve the two negative controls and their triggered false-positive boundary, and keep the
  four-case fixture smoke-only. The 750-case stratified pack, blinded dual review, adjudication
  and untouched holdout remain required before evidence or policy use.
- **Group C, dashboard review:** the tested browser/device baseline is accepted within its scope;
  automated browser, keyboard, focus and axe checks remain regression evidence, not universal WCAG
  certification. Re-review is required after material UI changes.
- **Group D, OSF and Hugging Face preparation:** prepare and validate the OSF protocol/report
  and Hugging Face dataset/Space candidate packages. Private OSF staging, an OSF draft
  registration, and governed Hugging Face Space metadata reconciliation are approved; public
  registration, dataset payload publication and paper publication remain gated.

Paper, preprint, manuscript and other publication submission remains explicitly deferred until
the final gate.

## Merge and release boundary

The owner-approved boundary is fail-closed: do not bypass review, merge, tag, sign,
attest or publish a release
while evidence, policy and source-licence gates remain unresolved. The verified
local handoff bundle is the current release artefact.

## External pre-publication actions (2026-07-20)

The repository owner is the accountable reviewer for the approved pre-publication
scope. The following external preparation actions were completed without publishing
  papers or making the research package public:

- OSF CLI: the pinned `edithatogo/osf-cli-go v1.0.0` was used with private OSF
  project `q8cnx`. The reviewed protocol, provenance, freeze, manifest, data-package
  and RO-Crate files were uploaded privately. The owner selected **OSF Preregistration**
  as the appropriate template, and an OSF draft was created. The draft remains
  unregistered and private pending protocol freeze and registration review.
- Hugging Face: the Space metadata was reconciled through the authenticated account
  to `license: apache-2.0` and `sdk: static`. The dataset remains governed as
  `license: other`; no dataset payload or raw source was uploaded. The destination
  check reports zero mismatches.
- Source and evidence scope: the owner approved derived-only historical MBS/PBS
  processing, CMS numeric/payment fields with AMA/CPT descriptors excluded, mapping
  calibration review, and dashboard review. These approvals do not convert the
  smoke fixture or prototype evidence into evidence-ready findings without the
  documented review and holdout steps.

The owner explicitly deferred paper, preprint, manuscript and public research-package
publication. No token or secret is stored in the repository.
