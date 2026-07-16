# Review Decisions

This checklist is the human/external boundary for the current release candidate.
Local implementation must not convert any `pending` decision to `approved` automatically.

| Decision | Current state | Evidence | Unblock action |
| --- | --- | --- | --- |
| Code versus data licensing | decided | `docs/LICENSING.md`, `data/seed/source_registry.*` | Keep project code/documentation Apache-2.0; apply CMS/AMA and other provider terms to source data. |
| CMS CLFS/CPT fields | pending human review | `data/derived/source_contracts/source_contract_validation.jsonl` | Confirm which payment/metadata fields may be retained or published; exclude descriptors unless expressly permitted. |
| Mapping calibration | pending human adjudication | `data/derived/vertical_slice/mapping_calibration_gate.json` | Review two positive and two negative controls and approve a research-specific threshold. |
| OSF protocol package | prepared, unpublished; private project `q8cnx` configured | `data/derived/osf/sync_manifest.jsonl`, OSF workflow run `29420960724` | Approve protocol and rows before changing `publish_allowed`. |
| Hugging Face dataset/Space | validated, unpublished; credentialed dry run passed | `scripts/check_huggingface_bundle.py`, workflow run `29420958930` | Approve licence/evidence gates before remote publication. |
| Zenodo DOI | deferred | `data/derived/release_readiness/summary.json` | Approve only after evidence, licence, OSF and research gates pass. |
| Historical MBS/PBS expansion | pending source review | `data/derived/final_handoff/final_handoff_tasks.jsonl` | Approve historical URLs, source terms and a reviewed PBS extract before processing. |
| PBS public API acquisition | public-user key path validated; July 2026 schedule acquired unreviewed | `docs/PBS_API_ACQUISITION.md`, `data/derived/source_downloads/pbs_api_acquisition.jsonl`, GitHub issue [#25](https://github.com/edithatogo/reimbursement-atlas/issues/25) | Copy the current public key from the official catalogue at runtime, fetch `/schedules` before `/items` and `/fees`, then review the selected monthly fields and source terms before promotion or publication. |
| July 2026 MBS TXT pair | bundle validated; official terms recorded; pending human licence/domain review | `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/validation_report.json`, `docs/SOURCE_LICENCE_EVIDENCE.md`, issue [#23](https://github.com/edithatogo/reimbursement-atlas/issues/23) | Confirm whether the intended derived fields may be redistributed under the MBS notice or obtain written Commonwealth approval; preserve attribution/notices and review descriptor-only rows before any evidence or public-release claim. |
| Dashboard visual baselines | Chromium smoke passed; cross-platform review pending | `docs/DASHBOARD_VALIDATION.md` | Review supported browser/OS screenshots; do not treat macOS smoke evidence as cross-platform approval. |
| Artifact-level licence review | queue generated; 159 candidates pending across project metadata, governance outputs and source-derived artefacts | `data/derived/licence_review/` | Review each checksum-bound candidate, record source terms, attribution, redistribution permission, restrictions and named approval before changing any publication gate. Do not treat the total as a source-file count. |

Current local proof remains separate from these decisions: repository release readiness is
green, while evidence, policy-claim, research-publication and archival readiness remain
fail-closed.
