# Review Decisions

This checklist is the human/external boundary for the current release candidate.
Local implementation must not convert any `pending` decision to `approved` automatically.

| Decision | Current state | Evidence | Unblock action |
| --- | --- | --- | --- |
| Code versus data licensing | decided | `docs/LICENSING.md`, `data/seed/source_registry.*` | Keep project code/documentation Apache-2.0; apply CMS/AMA and other provider terms to source data. |
| CMS CLFS/CPT fields | pending human review | `data/derived/source_contracts/source_contract_validation.jsonl` | Confirm which payment/metadata fields may be retained or published; exclude descriptors unless expressly permitted. |
| Mapping calibration | pending human adjudication | `data/derived/vertical_slice/mapping_calibration_gate.json` | Review two positive and two negative controls and approve a research-specific threshold. |
| OSF protocol package | prepared, unpublished; private project `q8cnx` configured | `data/derived/osf/sync_manifest.jsonl`, [OSF workflow run 29569972259](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972259) | Approve protocol and rows before changing `publish_allowed`; the current run performed no mutation. |
| Hugging Face dataset/Space | validated, unpublished; destination drift recorded | `scripts/check_huggingface_bundle.py`, [destination monitor run 29569184790](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569184790) | Reconcile the Space metadata only after licence/evidence gates pass; the current monitor performed no mutation. |
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
