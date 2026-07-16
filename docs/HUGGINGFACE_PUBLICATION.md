# Hugging Face publication plan

The repo records two Hugging Face targets:

1. **Dataset**: licence-safe derived metadata and analysis outputs listed in `data/derived/publication_manifest.json`.
2. **Space**: static Astro dashboard built from dashboard-safe CSV files under `apps/dashboard/public/data/`.

The workflow is token-gated through `HF_TOKEN`, `HF_DATASET_REPO` and `HF_SPACE_REPO`. It remains dry-run-safe until licence gates and release-readiness gates pass.

The release candidate bundle also includes `infra/huggingface/DATASET_CARD.md`,
`infra/huggingface/README.md` and `infra/huggingface/SPACE_README.md` so the dataset
card and Space metadata stay versioned with the publication manifest.

Live HF targets currently provisioned from this repository:

- Dataset: `edithatogo/reimbursement-atlas`
- Space: `edithatogo/reimbursement-atlas`

The dataset/Space creation flow is still separate from the GitHub Actions dry-run.
The repository secret is now configured and the dry-run has passed; publication remains
blocked until the workflow's licence, research, evidence and policy gates pass.

## Latest destination verification

On 2026-07-16, the public API confirmed that both configured targets exist. The dataset
currently contains only its README, license and Git attributes, and reports `mit` in its
remote card metadata. The Space is running a Gradio scaffold with `app.py` and also reports
MIT metadata. These destinations do not yet match the governed release candidates: the
dataset card preserves source-specific licences, while the Space candidate is a static
Astro dashboard with Apache-2.0 code metadata. This is destination drift, not publication
evidence. Reconciliation must occur through the gated workflow after licence and research
review; no remote mutation was performed during this verification.

Before either publication job can mutate a remote repository, the workflow runs
`scripts/check_huggingface_bundle.py`. It verifies the Space metadata, dashboard status contract,
publication manifest and forbidden raw/secret/local-path markers. A passing bundle check does not
grant permission to publish or imply evidence readiness. The mutation jobs also run
`scripts/check_huggingface_publication_gates.py`, which fails closed unless release readiness,
protocol status, source contracts, data quality, licence gates and policy/evidence flags all pass.

No raw restricted schedules, CPT descriptors, local ontology dumps or confidential prices should be published to Hugging Face.
