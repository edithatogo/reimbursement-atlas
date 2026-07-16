# Session v116: Hugging Face destination drift monitor

## Objective

Convert the observed Hugging Face destination mismatch into a repeatable, credential-free
monitor without weakening the publication gates or mutating either remote repository.

## Implemented

- Added `scripts/check_huggingface_destination.py`, which queries only the public Hugging Face
  API and emits redacted dataset/Space identity and card-field observations.
- Added SHA-pinned scheduled/manual workflow `.github/workflows/huggingface-destination.yml` with
  `contents: read`, no token, no clone, and no write-enabled publication step.
- Added unit coverage for read-only behavior and Space metadata drift detection.
- Added Pixi task `hf-destination` and documented the workflow and its fail-closed boundary.
- Added live issue #322 and Project #18 item; linked implementation back to blocker #320.
- Regenerated Conductor, GitHub Project, dashboard, seed-lake, data-dictionary, licence-review,
  source-drift, release-readiness and research-package projections.

## Verification

- Current public API observation: dataset metadata matches the governed `other` data-card
  contract; Space metadata remains `MIT`/`gradio` and therefore reports drift.
- `mutation_performed=false` is enforced in the report contract.
- Remote publication remains blocked by licence, research, evidence and policy-claim gates.
