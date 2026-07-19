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
Local implementation must not convert any `pending` decision to `approved` automatically.

| Decision | Current state | Evidence | Unblock action |
| --- | --- | --- | --- |
| Code versus data licensing | decided | `docs/LICENSING.md`, `data/seed/source_registry.*` | Keep project code/documentation Apache-2.0; apply CMS/AMA and other provider terms to source data. |
| CMS CLFS/CPT fields | owner-approved bounded derived scope; source publication remains gated | `data/derived/source_contracts/source_contract_validation.jsonl`, `docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md` | Retain only permitted numeric payment/RVU/locality/effective-date/source-version fields and provenance; exclude CPT/HCPCS descriptors, restricted crosswalks, raw files, credentials, coverage conclusions and net-price claims. Revalidate exact source terms before publication. |
| Mapping calibration | owner-approved protocol; current benchmark remains smoke-only and evidence gate remains review-required | `docs/MAPPING_CALIBRATION_PROTOCOL.md`, `data/mapping_review/decisions.jsonl`, `data/derived/vertical_slice/mapping_calibration_gate.json` | Build the source-stratified 750-case pack, complete blinded dual review and adjudication, then evaluate the untouched holdout before policy use. |
| OSF protocol package | owner-approved local-only non-paper staging; no remote mutation | `data/derived/osf/sync_manifest.jsonl`, [OSF workflow run 29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259) | Keep protocols, reports and research-package artefacts local; do not upload, register or publish while paper publication is excluded. |
| Hugging Face dataset/Space | owner-approved local-only preparation; no remote mutation | `scripts/check_huggingface_bundle.py`, [destination monitor run 29569184790](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569184790) | Keep candidate dataset/Space bundles local and retain the documented metadata drift; do not write, publish or correct remote metadata without separate authorization. |
| Zenodo DOI | owner-approved local-only archive; no deposit | `data/derived/release_readiness/summary.json`, [Zenodo preflight run 29569972301](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972301) | Retain the verified local bundle/archive and checksums; do not deposit or mint a DOI until evidence, licence, OSF and policy gates pass. |
| Historical MBS/PBS expansion | owner-approved metadata and local-cache scope; parsing/publication remain gated | `data/derived/final_handoff/final_handoff_tasks.jsonl`, `data/derived/historical_sources/summary.json` | Track catalogue metadata, URLs, dates, checksums and acquisition attempts; retain raw files only in ignored local storage; require source-specific reuse decisions before parsing or publication. |
| PBS public API acquisition | public-user key path validated; July 2026 schedule acquired unreviewed | `docs/PBS_API_ACQUISITION.md`, `data/derived/source_downloads/pbs_api_acquisition.jsonl`, GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25) | Copy the current public key from the official catalogue at runtime, fetch `/schedules` before `/items` and `/fees`, then review the selected monthly fields and source terms before promotion or publication. |
| July 2026 MBS TXT pair | bundle validated; official terms recorded; pending human licence/domain review | `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/validation_report.json`, `docs/SOURCE_LICENCE_EVIDENCE.md`, issue [#23](https://github.com/edithatogo/reimbursement-atlas/issues/23) | Confirm whether the intended derived fields may be redistributed under the MBS notice or obtain written Commonwealth approval; preserve attribution/notices and review descriptor-only rows before any evidence or public-release claim. |
| Dashboard visual baselines | owner-approved tested baseline; formal WCAG conformance not claimed | `docs/DASHBOARD_VALIDATION.md`, issue [#188](https://github.com/edithatogo/reimbursement-atlas/issues/188) | Retain the cross-browser automated evidence and re-review after material UI changes; automated axe/screenshot results remain scoped evidence, not a universal accessibility certification. |
| Artifact-level licence review | owner-approved scope; 177 checksum-bound decisions recorded and validated | `data/licence_review/decisions.jsonl`; `data/derived/licence_review/`; `docs/LICENCE_DECISION_MATRIX.md` | Decisions apply only to the exact path/checksum and documented scope. The generated queue remains `pending` on regeneration by design; validate the companion decisions file before changing any publication gate. Do not treat the total as a source-file count. |

Current local proof remains separate from these decisions: repository release readiness is
green, while evidence, policy-claim, research-publication and archival readiness remain
fail-closed.

The current decision file records `approved` for each exact candidate under the approved
derived/metadata scope. It does not approve raw payloads, restricted descriptors,
confidential values, unsupported claims, or any later checksum change.
