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
| CMS CLFS/CPT fields | pending human review | `data/derived/source_contracts/source_contract_validation.jsonl` | Confirm which payment/metadata fields may be retained or published; exclude descriptors unless expressly permitted. |
| Mapping calibration | owner-approved benchmark outcomes; evidence gate remains review-required | `data/mapping_review/decisions.jsonl`, `data/derived/vertical_slice/mapping_calibration_gate.json` | Preserve the four exact decisions and complete any separate qualified-domain/evidence review before policy use. |
| OSF protocol package | owner-approved for non-paper staging; unpublished and fail-closed | `data/derived/osf/sync_manifest.jsonl`, [OSF workflow run 29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259) | Keep papers/preprints unpublished; complete the protocol freeze, remote snapshot and token-gated sync only after the remaining technical gates pass. |
| Hugging Face dataset/Space | owner-approved preparation; unpublished; destination drift recorded | `scripts/check_huggingface_bundle.py`, [destination monitor run 29569184790](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569184790) | Reconcile governed Space metadata and run the token-gated workflow; do not publish papers or manuscripts. |
| Zenodo DOI | deferred | `data/derived/release_readiness/summary.json`, [Zenodo preflight run 29569972301](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972301) | Approve only after evidence, licence, OSF and research gates pass; the current preflight performed no deposit. |
| Historical MBS/PBS expansion | pending source review | `data/derived/final_handoff/final_handoff_tasks.jsonl` | Approve historical URLs, source terms and a reviewed PBS extract before processing. |
| PBS public API acquisition | public-user key path validated; July 2026 schedule acquired unreviewed | `docs/PBS_API_ACQUISITION.md`, `data/derived/source_downloads/pbs_api_acquisition.jsonl`, GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25) | Copy the current public key from the official catalogue at runtime, fetch `/schedules` before `/items` and `/fees`, then review the selected monthly fields and source terms before promotion or publication. |
| July 2026 MBS TXT pair | bundle validated; official terms recorded; pending human licence/domain review | `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/validation_report.json`, `docs/SOURCE_LICENCE_EVIDENCE.md`, issue [#23](https://github.com/edithatogo/reimbursement-atlas/issues/23) | Confirm whether the intended derived fields may be redistributed under the MBS notice or obtain written Commonwealth approval; preserve attribution/notices and review descriptor-only rows before any evidence or public-release claim. |
| Dashboard visual baselines | Chromium smoke passed; cross-platform review pending | `docs/DASHBOARD_VALIDATION.md` | Review supported browser/OS screenshots; do not treat macOS smoke evidence as cross-platform approval. |
| Artifact-level licence review | owner-approved scope; 177 checksum-bound decisions recorded and validated | `data/licence_review/decisions.jsonl`; `data/derived/licence_review/`; `docs/LICENCE_DECISION_MATRIX.md` | Decisions apply only to the exact path/checksum and documented scope. The generated queue remains `pending` on regeneration by design; validate the companion decisions file before changing any publication gate. Do not treat the total as a source-file count. |

Current local proof remains separate from these decisions: repository release readiness is
green, while evidence, policy-claim, research-publication and archival readiness remain
fail-closed.

The current decision file records `approved` for each exact candidate under the approved
derived/metadata scope. It does not approve raw payloads, restricted descriptors,
confidential values, unsupported claims, or any later checksum change.
