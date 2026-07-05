# Hugging Face publication plan

The repo records two Hugging Face targets:

1. **Dataset**: licence-safe derived metadata and analysis outputs listed in `data/derived/publication_manifest.json`.
2. **Space**: static Astro dashboard built from dashboard-safe CSV files under `apps/dashboard/public/data/`.

The workflow is token-gated through `HF_TOKEN`, `HF_DATASET_REPO` and `HF_SPACE_REPO`. It remains dry-run-safe until licence gates and release-readiness gates pass.

The release candidate bundle also includes `infra/huggingface/DATASET_CARD.md`,
`infra/huggingface/README.md` and `infra/huggingface/SPACE_README.md` so the dataset
card and Space metadata stay versioned with the publication manifest.

No raw restricted schedules, CPT descriptors, local ontology dumps or confidential prices should be published to Hugging Face.
