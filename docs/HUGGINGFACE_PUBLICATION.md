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
That dry-run remains token-gated and should stay blocked until the workflow secrets
and publication review gates are available.

Before either publication job can mutate a remote repository, the workflow runs
`scripts/check_huggingface_bundle.py`. It verifies the Space metadata, dashboard status contract,
publication manifest and forbidden raw/secret/local-path markers. A passing bundle check does not
grant permission to publish or imply evidence readiness.

No raw restricted schedules, CPT descriptors, local ontology dumps or confidential prices should be published to Hugging Face.
