# OSF workflow

OSF is the planned home for research protocols, detailed reports, appendices and preprint staging. GitHub remains the implementation repository. Hugging Face hosts licence-safe derived datasets and the dashboard.

Generated artefacts:

- `data/derived/osf/component_plan.*`
- `data/derived/osf/osf_publication_manifest.json`
- `protocols/*.md`
- `reports/*.md`

Publication rules:

1. Upload protocols and reports before or alongside public releases.
2. Do not upload raw restricted source files unless a licence review explicitly permits it.
3. Use OSF components to separate protocols, reports, appendices, preprints and reproducibility packages.
4. Keep OSF publication token-gated and dry-run by default in CI.
