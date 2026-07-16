# v128 Hugging Face destination drift preflight

## Scope

Refresh read-only OSF, Hugging Face and Zenodo publication preflight evidence and investigate the
Hugging Face destination monitor failure without mutating any external project.

## Results

- OSF workflow `29529140438`: success; pinned `osf-cli-go v1.0.0` contract passed and sync rows
  remained fail-closed.
- Hugging Face workflow `29529142063`: success; candidate validation passed and both publication
  jobs were skipped.
- Zenodo workflow `29529145184`: success; non-depositing preflight passed.
- Hugging Face destination workflow `29529143659`: expected drift failure; dataset metadata passed,
  while the existing Space reported `license=mit` and `sdk=gradio` instead of `apache-2.0` and
  `static`.

## Decision

Do not mutate or repurpose the existing Space. Preserve `mutation_performed=false`, keep publication
fail-closed, and attach the evidence to issues #320 and #322 until the licence, evidence, research,
policy and explicit publication gates are approved.
